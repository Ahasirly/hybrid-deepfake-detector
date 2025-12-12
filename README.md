# Hybrid Deepfake Detection System

## Project Architecture

```
├── backend/                 # FastAPI Backend (Deploy to AWS)
│   ├── app/
│   │   ├── api/v1/         # API Routes
│   │   ├── models/         # ML Model Loaders (SBI, DistilDIRE)
│   │   ├── services/       # Business Logic
│   │   └── core/           # Configuration
│   ├── ml_models/          # Fine-tuned Model Files
│   └── requirements.txt
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # UI Components
│   │   ├── pages/          # Pages
│   │   └── services/       # API Calls
│   └── package.json
└── docker/                 # Docker Deployment Config
```

## Models

1. **SBI (Fine-tuned)** - Self-Blended Images
2. **DistilDIRE (Fine-tuned)** - Distilled Diffusion Reconstruction Error  
3. **ChatGPT Vision API** - VLM Verification

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
