from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Deepfake Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境要改
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: 导入路由
# from app.api.v1 import detection
# app.include_router(detection.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
