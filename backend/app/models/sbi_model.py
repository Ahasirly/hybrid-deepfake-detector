import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import sys

# Add ml_inference to path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml_inference'))

from sbi.inference.model import Detector


class SBIModel:
    """
    SBI (Self-Blended Images) deepfake detection model

    Uses fine-tuned EfficientNet-B4 (exp003_multi_dataset):
    - Trained on FFHQ + LFW + CelebA-HQ
    - Input size: 380x380
    - Performance: AUC 98.73%, Accuracy 94.83%
    """

    def __init__(self, model_path: str):
        """
        Initialize SBI model

        Args:
            model_path: Path to the model directory containing:
                - exp003_best_model.pth (fine-tuned weights)
                - adv-efficientnet-b4-44fb3a87.pth (backbone weights)
        """
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize model architecture
        self.model = Detector()

        # Load fine-tuned weights
        checkpoint_path = os.path.join(model_path, 'exp003_best_model.pth')

        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"SBI model checkpoint not found at {checkpoint_path}. "
                f"Please ensure exp003_best_model.pth is in {model_path}"
            )

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint)

        # Move to device and set to eval mode
        self.model = self.model.to(self.device)
        self.model.eval()

        # Image preprocessing (exp003 uses 380x380)
        self.transform = transforms.Compose([
            transforms.Resize((380, 380)),
            transforms.ToTensor(),
            # Note: No additional normalization needed, model handles internally
        ])

        print(f"✓ SBI model loaded successfully on {self.device}")

    def predict(self, image_bytes: bytes) -> tuple[bool, float]:
        """
        Predict if image is a deepfake

        Args:
            image_bytes: Image file bytes (JPEG, PNG, etc.)

        Returns:
            tuple: (is_fake: bool, confidence: float)
                - is_fake: True if predicted as fake, False if real
                - confidence: Probability of being fake (0.0 to 1.0)
        """
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)

            # Inference
            with torch.no_grad():
                output = self.model(img_tensor)
                # Apply softmax to get probabilities
                probs = torch.nn.functional.softmax(output, dim=1)
                # Get fake probability (class 1)
                fake_prob = probs[0, 1].item()

            # Threshold at 0.5
            is_fake = fake_prob > 0.5

            return is_fake, fake_prob

        except Exception as e:
            print(f"Error in SBI prediction: {e}")
            # Return neutral prediction on error
            return False, 0.5
