# ConstructGuard AI v3.0

Autonomous Construction Site Safety Monitor powered by **Qwen3.6-27B** running on **AMD MI300X**.

Built for the **AMD Developer Hackathon 2026** (lablab.ai).

## 🚀 Features
- **Vision Agent**: Detects workers, helmets, vests, harnesses with bounding boxes.
- **Reasoning Agent**: Explains *why* violations are dangerous in natural language with OSHA references.
- **Risk Scorer**: Evaluates severity and calculates composite risk scores.
- **Site Memory**: SQLite-based memory that detects systemic issues and escalates emergencies.
- **PDF Reports**: Automatically generates downloadable compliance reports.

## 🛠 Tech Stack
- **AI Model**: Qwen3.6-27B (Open Source)
- **Hardware**: AMD MI300X via ROCm
- **Backend**: FastAPI + Python + OpenCV + ReportLab
- **Frontend**: React + Vite + TailwindCSS

## 💻 Local Development (Mock Mode)
To build and run locally without a GPU, the system defaults to "Mock Mode", simulating the AI inference.

### 1. Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:5173`.

## ☁️ AMD Cloud Deployment (Production)
When deploying to the AMD Developer Cloud, run the full stack via Docker Compose. The backend will automatically download the model to the MI300X GPU.

```bash
docker-compose up -d --build
```
Access the production application on port 80 of your AMD cloud instance.

## 📁 Architecture
```
constructguard-ai/
├── backend/          # FastAPI, Agents, Models, OpenCV logic
├── frontend/         # React dashboard
├── docker-compose.yml# AMD ROCm-enabled container orchestration
└── README.md
```
