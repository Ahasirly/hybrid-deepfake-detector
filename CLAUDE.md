# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid deepfake detection system that combines three ML approaches:
- **SBI (Self-Blended Images)** - Fine-tuned model for detecting self-blended image artifacts
- **DistilDIRE** - Fine-tuned distilled diffusion reconstruction error model
- **ChatGPT Vision API** - VLM-based verification layer

The system follows a FastAPI backend + React frontend architecture designed for AWS deployment.

## Development Commands

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

For development with auto-reload on port 8000 (default).

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### Environment Setup

Create a `.env` file in the `backend/` directory with:
```
OPENAI_API_KEY=your_key_here
MODEL_SBI_PATH=./ml_models/sbi_finetuned
MODEL_DISTILDIRE_PATH=./ml_models/distildire_finetuned
```

## Architecture

### Backend Structure

- `app/main.py` - FastAPI application entry point with CORS middleware
- `app/core/config.py` - Pydantic settings loading from `.env`
- `app/api/v1/endpoints/detection.py` - Detection endpoint (currently stubbed)
- `app/models/` - Model loader classes for SBI, DistilDIRE, and ChatGPT Vision
- `app/services/detection_service.py` - Orchestration layer combining all three models
- `ml_models/` - Directory for fine-tuned model weights (`.pth`, `.pt`, `.onnx` files excluded from git)

### Detection Flow

The intended detection pipeline (currently incomplete):
1. User uploads image via `/api/v1/detect` endpoint
2. `DetectionService` coordinates the three models:
   - SBI model returns `(is_fake: bool, confidence: float)`
   - DistilDIRE model returns `(is_fake: bool, confidence: float)`
   - ChatGPT Vision API provides additional verification
3. Results are combined and returned to frontend

### Model Integration Pattern

Each model class follows this interface:
```python
class ModelName:
    def __init__(self, model_path: str):
        # Load model from path

    def predict(self, image) -> tuple[bool, float]:
        # Return (is_fake, confidence)
```

The `ChatGPTVision` class uses OpenAI client and expects base64-encoded images.

### Key Dependencies

- FastAPI + Uvicorn for API server
- PyTorch/TorchVision for ML models
- OpenAI Python SDK for GPT-4 Vision
- Boto3 for AWS integration (deployment)
- Pydantic for configuration and validation

## Current State

The codebase is a skeleton structure with TODOs marking implementation points:
- Model loaders are stubbed
- Detection service orchestration is not implemented
- API endpoint returns placeholder responses
- Router is not yet included in main app (commented out in `app/main.py:14-16`)

When implementing:
1. Start by implementing individual model loaders in `app/models/`
2. Integrate models into `DetectionService`
3. Wire up the detection endpoint
4. Uncomment router registration in `main.py`
