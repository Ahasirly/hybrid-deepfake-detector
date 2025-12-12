from app.models.chatgpt_vision import ChatGPTVision
from app.core.config import settings

class DetectionService:
    def __init__(self):
        # Initialize ChatGPT Vision model
        self.chatgpt_vision = ChatGPTVision(api_key=settings.OPENAI_API_KEY)

        # TODO: Initialize SBI and DistilDIRE models when ready
        # self.sbi_model = SBIModel(settings.MODEL_SBI_PATH)
        # self.distildire_model = DistilDIREModel(settings.MODEL_DISTILDIRE_PATH)

    def detect(self, image_bytes: bytes) -> dict:
        """
        Detect deepfake using hybrid approach

        Args:
            image_bytes: Image file bytes

        Returns:
            dict: Detection results with confidence scores
        """

        # TODO: For now, only ChatGPT Vision is implemented
        # SBI and DistilDIRE will return placeholder results

        # 1. SBI Model (placeholder)
        sbi_is_fake = False
        sbi_confidence = 0.5

        # 2. DistilDIRE Model (placeholder)
        distildire_is_fake = False
        distildire_confidence = 0.5

        # 3. ChatGPT Vision (real)
        chatgpt_is_fake, chatgpt_confidence = self.chatgpt_vision.verify(image_bytes)

        # 4. Combine results (weighted average)
        # For now, we'll give more weight to ChatGPT since it's the only real model
        total_weight = 3.0  # Will be evenly distributed when all models are active

        # Calculate weighted confidence
        if chatgpt_is_fake:
            final_confidence = chatgpt_confidence
            is_fake = True
        else:
            final_confidence = 1 - chatgpt_confidence
            is_fake = False

        return {
            "is_fake": is_fake,
            "confidence": final_confidence,
            "models": {
                "sbi": {
                    "is_fake": sbi_is_fake,
                    "confidence": sbi_confidence,
                    "status": "placeholder"
                },
                "distildire": {
                    "is_fake": distildire_is_fake,
                    "confidence": distildire_confidence,
                    "status": "placeholder"
                },
                "chatgpt": {
                    "is_fake": chatgpt_is_fake,
                    "confidence": chatgpt_confidence,
                    "status": "active"
                }
            }
        }
