# LawGenie AI

LawGenie AI is a full-stack legal assistant platform for Indian law research and document-aware Q&A.
It combines a FastAPI backend for retrieval, training, and chat sessions with a React + Vite frontend for an interactive user experience.

## Features

- Legal Q&A chat with conversation history
- JWT-based session continuity for chat users
- MongoDB-backed document storage and retrieval
- Training pipeline to ingest and index legal data (optional, separate service)
- Search endpoint with multiple retrieval modes
- Responsive React interface with theme support
- **Two-part architecture**: Chat and Training services run independently

## Repository Structure

```text
LawGenie-AI/
├─ Backend/                  # FastAPI app, retrieval pipeline, training logic
├─ Frontend/                 # React + Vite web app
├─ pdfs/                     # Project-level PDF assets
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
├─ SECURITY.md
├─ CHANGELOG.md
└─ README.md
```

## Tech Stack

### Backend

- Python
- FastAPI + Uvicorn
- MongoDB (PyMongo)
- Groq API client
- Sentence Transformers / Torch

### Frontend

- React 19
- Vite 7
- Tailwind CSS 4
- React Router 7
- Axios

## Prerequisites

- Python 3.10+
- Node.js 20+
- npm 10+
- MongoDB (local or Atlas)

## Quick Start

### 1) Clone and open project

```bash
git clone <your-repo-url>
cd LawGenie-AI
```

### 2) Backend setup

```bash
cd Backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `Backend/.env` and set required values:

```env
GROQ_API_KEY=your_groq_key
JWT_SECRET_KEY=your_jwt_secret
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=lawgenie
GROQ_MODEL=openai/gpt-oss-120b
```

**Run Chat Service (Main Deployment):**

```bash
uvicorn main:app --reload
```

Backend docs: `http://127.0.0.1:8000/docs`

**Optional: Run Training Service (Terminal 2):**

```bash
uvicorn training_service:training_app --port 8001 --reload
```

Training docs: `http://127.0.0.1:8001/docs`

**Backend is now split into two services:**
- `main.py` (Chat + Search) - Always needed, port 8000
- `training_service.py` (Training) - Optional, port 8001

See [Backend/TWO_PART_ARCHITECTURE.md](Backend/TWO_PART_ARCHITECTURE.md) for details.

### 3) Frontend setup

Open a new terminal:

```bash
cd Frontend
npm install
```

Create `Frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run frontend:

```bash
npm run dev
```

Default Vite URL is shown in terminal (commonly `http://localhost:5173` or `http://localhost:5178`).

## API Overview

Base URL: `http://127.0.0.1:8000`

- `GET /chat/?q=...` - Ask legal query and get AI response
- `GET /chat/history` - Get chat history for bearer token
- `GET /search/?q=...&top_k=5&mode=auto` - Search indexed legal corpus
- `POST /train/` - Trigger training/ingestion pipeline

## Development Notes

- Backend CORS currently allows selected localhost origins.
- Frontend API layer is in `Frontend/src/api` and `Frontend/src/services`.
- Chat authorization uses `Authorization: Bearer <token>` when available.

## Contributing

Please read `CONTRIBUTING.md` before opening issues or pull requests.

## Security

To report vulnerabilities, see `SECURITY.md`.

## License

This project is licensed under the terms in `LICENSE`.
