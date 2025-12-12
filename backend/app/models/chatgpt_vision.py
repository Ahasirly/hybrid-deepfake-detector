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
            tuple[bool, float]: (is_fake, confidence)
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
1. An authentic, unmodified photograph
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
- is_fake: true if you believe it's AI-generated/deepfake, false if authentic
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

            return result.get("is_fake", False), result.get("confidence", 0.0)

        except Exception as e:
            print(f"[ERROR] ChatGPT Vision error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return conservative result on error
            return False, 0.0
