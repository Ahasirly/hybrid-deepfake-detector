# TODO: 实现检测 API
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/detect")
async def detect_deepfake(file: UploadFile = File(...)):
    """
    接收图片，返回检测结果
    1. SBI 模型预测
    2. DistilDIRE 模型预测
    3. ChatGPT Vision 验证
    4. 综合结果
    """
    # TODO: 实现
    return {"is_fake": False, "confidence": 0.0}
