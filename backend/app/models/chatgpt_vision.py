# TODO: ChatGPT Vision API 调用
from openai import OpenAI

class ChatGPTVision:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def verify(self, image_base64: str) -> dict:
        # TODO: 调用 GPT-4 Vision 分析图片
        pass
