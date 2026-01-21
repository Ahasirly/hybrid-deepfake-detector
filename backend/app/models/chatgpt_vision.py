from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

class ChatGPTVision:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def verify(self, image_bytes: bytes) -> tuple[bool, float]:
        """
        Analyze image using GPT-4 Vision to detect deepfakes

        Args:
            image_bytes: Image bytes

        Returns:
            tuple[bool, float]: (is_fake, deepfake_confidence)
                - is_fake: True if detected as deepfake, False if real
                - deepfake_confidence: Probability of being fake (0.0-1.0)
        """
        # Convert bytes to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        try:
            print(f"[DEBUG] Calling ChatGPT Vision API...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are an expert at detecting AI-generated or manipulated images (deepfakes).

Analyze this image carefully and determine if it appears to be:
1. A real, unmodified photograph
2. An AI-generated or deepfake image

Look for signs such as:
- Unnatural facial features or proportions
- Inconsistent lighting or shadows
- Artifacts around edges or details
- Unnatural textures or patterns
- Unrealistic backgrounds
- Blending issues

Respond ONLY with a JSON object in this exact format:
{"is_fake": true/false, "confidence": 0.0-1.0, "reasoning": "brief explanation"}

Where:
- is_fake: true if you believe it's AI-generated/deepfake, false if real
- confidence: your confidence level (0.0 = not confident, 1.0 = very confident)
- reasoning: brief explanation of your decision"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            # Parse response
            import json
            result_text = response.choices[0].message.content
            print(f"[DEBUG] ChatGPT response: {result_text}")

            # Extract JSON from response (sometimes GPT adds markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Convert GPT's confidence to deepfake_confidence (probability of being fake)
            # If is_fake=True, confidence=0.9 means "90% sure it's fake" → deepfake_confidence = 0.9
            # If is_fake=False, confidence=0.9 means "90% sure it's real" → deepfake_confidence = 0.1
            is_fake_raw = result.get("is_fake", False)
            confidence_raw = result.get("confidence", 0.0)

            if is_fake_raw:
                # GPT says it's fake: confidence directly represents deepfake probability
                deepfake_confidence = confidence_raw
            else:
                # GPT says it's real: confidence represents real probability
                # Convert to deepfake probability: deepfake_confidence = 1 - real_confidence
                deepfake_confidence = 1.0 - confidence_raw

            # Determine final is_fake based on deepfake_confidence
            is_fake_final = deepfake_confidence > 0.5

            return is_fake_final, deepfake_confidence

        except Exception as e:
            print(f"[ERROR] ChatGPT Vision error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return conservative result on error
            return False, 0.0
