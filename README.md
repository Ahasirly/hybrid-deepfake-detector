# Hybrid Deepfake Detection System

A web-based deepfake detection system using a hybrid ensemble approach combining three AI models: SBI (Self-Blended Images), DistilDIRE, and ChatGPT Vision API.

## Project Status

### Implemented
- **Frontend**: React + Vite + Tailwind CSS (black & white minimalist design)
- **Backend API**: FastAPI with `/api/v1/detect` endpoint
- **ChatGPT Vision**: Fully functional deepfake detection using GPT-4o
- **SBI Model**: EfficientNet-B4 fine-tuned on FFHQ + LFW + CelebA-HQ (AUC 98.73%)
- **DistilDIRE Model**: ConvNeXt-base with CLIP-LAION2B pretraining (AP 96.11%)
- **Ensemble Fusion**: Weighted combination with adaptive strategy based on active models
- **Docker Deployment**: Full containerized deployment with docker-compose

### Model Availability
Models run in "placeholder" mode if weight files are not present. Download model weights to enable full functionality:
- SBI: `backend/ml_models/deployment_package/models/sbi/`
- DistilDIRE: `backend/ml_models/deployment_package/models/distildire/`

## Project Architecture

```
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/   # Detection endpoint
│   │   ├── models/             # ML Model Loaders
│   │   │   ├── sbi_model.py
│   │   │   ├── distildire_model.py
│   │   │   └── chatgpt_vision.py
│   │   ├── services/           # Detection orchestration
│   │   ├── ml_inference/       # Model architectures
│   │   │   ├── sbi/           # SBI detector architecture
│   │   │   └── improved_model.py  # DistilDIRE v2
│   │   └── core/               # Configuration
│   ├── ml_models/              # Model weight files
│   │   └── deployment_package/models/
│   │       ├── sbi/           # SBI weights
│   │       └── distildire/    # DistilDIRE weights
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # ImageUploader, ResultDisplay
│   │   ├── services/          # API client
│   │   └── App.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.js
└── docker-compose.yml          # Container orchestration
```

## Models

| Model | Architecture | Input Size | Performance |
|-------|-------------|------------|-------------|
| **SBI** | EfficientNet-B4 | 380×380 | AUC 98.73%, Acc 94.83% |
| **DistilDIRE v2** | ConvNeXt-base + CLIP | 224×224 | Acc 86.89%, AP 96.11% |
| **ChatGPT Vision** | GPT-4o | Auto | VLM reasoning |

### Ensemble Fusion Strategy

The system adapts based on available models:

- **3 Models Active**: SBI (30%) + DistilDIRE (35%) + ChatGPT (35%)
- **2 Models Active**: Weighted split based on model pair
- **1 Model Active**: Single model at 100%

Final decision threshold: confidence > 0.5 indicates deepfake

## Setup

### Quick Start with Docker (Recommended)

```bash
# Clone and configure
git clone <repo-url>
cd hybrid-deepfake-detector

# Set your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > backend/.env

# Build and run
docker-compose up -d --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API Key

#### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Drag and drop an image or click to upload
3. Wait for AI analysis
4. View detection results with confidence scores

## Features

- **Drag & Drop Upload**: Intuitive image upload interface
- **Automatic Compression**: Images up to 20MB are automatically compressed to optimize API calls
- **Real-time Detection**: Instant analysis using GPT-4o Vision
- **Detailed Results**: Confidence scores from each model
- **Responsive Design**: Clean black & white minimalist UI

## API Endpoint

**POST** `/api/v1/detect`

- **Input**: Image file (PNG, JPG, JPEG, WEBP, max 20MB)
- **Processing**: Auto-compressed to ~5MB for optimal API performance

**Response:**
```json
{
  "is_fake": false,
  "confidence": 0.85,
  "ensemble_mode": "3_models_active",
  "models": {
    "sbi": {
      "is_fake": false,
      "confidence": 0.82,
      "status": "active"
    },
    "distildire": {
      "is_fake": false,
      "confidence": 0.88,
      "status": "active"
    },
    "chatgpt": {
      "is_fake": false,
      "confidence": 0.85,
      "status": "active"
    }
  }
}
```

**Status Values:** `active`, `placeholder`, `error`

**Confidence Interpretation:** 0.0 = definitely real, 1.0 = definitely fake

## Tech Stack

**Frontend:**
- React 19 + Vite 7
- Tailwind CSS 3
- Axios + React Dropzone

**Backend:**
- FastAPI + Uvicorn
- PyTorch (CPU/GPU)
- OpenAI Python SDK
- EfficientNet-PyTorch (SBI)
- timm + huggingface-hub (DistilDIRE)

**Deployment:**
- Docker + Docker Compose

## GPU Support

Models auto-detect CUDA availability. For GPU inference:
- Local: Install PyTorch with CUDA support
- AWS: Use g4dn.xlarge or similar GPU instances

## Next Steps

1. Download and deploy model weight files
2. Add result visualization (heatmaps, artifact highlighting)
3. Production deployment with proper CORS configuration
4. Performance optimization and caching

## Model Weights

Download: [Google Drive](TODO)

Extract `deployment_package.tar.gz` to `backend/ml_models/`

## Credits

### Datasets
- [Swappir Dataset](https://huggingface.co/datasets/Sumsub/Swappir) - LFW, CelebA-HQ, FairFace
- [FFHQ](https://github.com/NVlabs/ffhq-dataset)
- [SimSwap](https://github.com/neuralchen/SimSwap)
- [Roop](https://github.com/s0md3v/roop)

### Code & Pretrained Models
- [EfficientNet-PyTorch](https://github.com/lukemelas/EfficientNet-PyTorch)
- [RetinaFace](https://github.com/ternaus/retinaface)
- [timm](https://github.com/huggingface/pytorch-image-models)
- [OpenAI API](https://platform.openai.com/)
