# Hybrid Deepfake Detection System

A web-based deepfake detection system using a hybrid approach combining three AI models: SBI, DistilDIRE, and ChatGPT Vision API.

## Project Status

### ✅ Implemented
- **Frontend**: React + Vite + Tailwind CSS (black & white minimalist design)
- **Backend API**: FastAPI with `/api/v1/detect` endpoint
- **ChatGPT Vision**: Fully functional deepfake detection using GPT-4o
- **Image Upload**: Drag & drop interface with preview
- **Results Display**: Confidence scores and model-specific results

### 🚧 In Progress
- **SBI Model**: Placeholder (to be deployed on AWS)
- **DistilDIRE Model**: Placeholder (to be deployed on AWS)

## Project Architecture

```
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API Routes
│   │   │   └── endpoints/  # Detection endpoint
│   │   ├── models/         # ML Model Loaders
│   │   │   ├── sbi_model.py
│   │   │   ├── distildire_model.py
│   │   │   └── chatgpt_vision.py
│   │   ├── services/       # Detection orchestration
│   │   └── core/           # Configuration
│   ├── ml_models/          # Fine-tuned Model Files
│   ├── requirements.txt
│   └── .env               # Environment variables
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # ImageUploader, ResultDisplay
│   │   ├── services/       # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── CLAUDE.md              # AI assistant documentation
```

## Models

1. **SBI (Self-Blended Images)** - Fine-tuned model for detecting self-blended artifacts
2. **DistilDIRE** - Distilled Diffusion Reconstruction Error model
3. **ChatGPT Vision (GPT-4o)** - VLM-based verification layer ✅ Active

## Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API Key

### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_key_here
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

Frontend runs at: **http://localhost:3000**

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
- **Processing**: Automatically compressed to ~5MB for optimal API performance
- **Output**:
```json
{
  "is_fake": false,
  "confidence": 0.85,
  "models": {
    "sbi": {
      "is_fake": false,
      "confidence": 0.5,
      "status": "placeholder"
    },
    "distildire": {
      "is_fake": false,
      "confidence": 0.5,
      "status": "placeholder"
    },
    "chatgpt": {
      "is_fake": false,
      "confidence": 0.85,
      "status": "active"
    }
  }
}
```

## Tech Stack

**Frontend**:
- React 19
- Vite 7
- Tailwind CSS 3
- Axios
- React Dropzone

**Backend**:
- FastAPI
- PyTorch
- OpenAI Python SDK
- Pydantic

**Deployment** (Planned):
- Frontend: AWS S3 + CloudFront
- Backend: AWS EC2/ECS
- Models: AWS for GPU inference

## Next Steps

1. Fine-tune SBI and DistilDIRE models
2. Deploy models to AWS
3. Implement weighted ensemble for final predictions
4. Add result visualization (heatmaps, artifacts highlighting)
5. Production deployment with proper CORS configuration
