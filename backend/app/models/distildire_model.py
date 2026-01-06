import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import sys

# Add ml_inference to path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml_inference'))

from improved_model import DistilDIREImproved


class DistilDIREModel:
    """
    DistilDIRE v2 deepfake detection model

    Uses ConvNeXt-base with CLIP-LAION2B pretraining:
    - Trained on Deepfake-Eval-2024 dataset
    - Input size: 224x224
    - Performance: Accuracy 86.89%, AP 96.11%
    """

    def __init__(self, model_path: str):
        """
        Initialize DistilDIRE model

        Args:
            model_path: Path to the model directory containing:
                - v2_best_model.pth (fine-tuned weights)
        """
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize model architecture
        self.model = DistilDIREImproved(
            device=self.device,
            backbone='convnext_base',
            use_clip=True,  # Use CLIP-LAION2B pretrained weights
            dropout=0.2
        )

        # Load fine-tuned weights
        checkpoint_path = os.path.join(model_path, 'v2_best_model.pth')

        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"DistilDIRE model checkpoint not found at {checkpoint_path}. "
                f"Please ensure v2_best_model.pth is in {model_path}"
            )

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])

        # Move to device and set to eval mode
        self.model = self.model.to(self.device)
        self.model.eval()

        # Image preprocessing (224x224 for ConvNeXt)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print(f"✓ DistilDIRE model loaded successfully on {self.device}")

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
                output = self.model(img_tensor, eps=None)  # v2 doesn't use eps
                logit = output['logit']
                # Apply sigmoid to convert logit to probability
                fake_prob = torch.sigmoid(logit).item()

            # Threshold at 0.5
            is_fake = fake_prob > 0.5

            return is_fake, fake_prob

        except Exception as e:
            print(f"Error in DistilDIRE prediction: {e}")
            # Return neutral prediction on error
            return False, 0.5
