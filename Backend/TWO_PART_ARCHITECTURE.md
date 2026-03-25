# LawGenie AI - Two-Part Architecture

This document explains how LawGenie AI is now split into two independent services.

## Architecture Overview

LawGenie AI is now structured as:

1. **Main Chat Service** (`main.py`) - Production deployment
   - Chat endpoint: `GET /chat/?q=...`
   - Search endpoint: `GET /search/?q=...`
   - Chat history: `GET /chat/history`

2. **Training Service** (`training_service.py`) - Optional, separate
   - Training endpoint: `POST /train/`
   - Runs independently from chat
   - Not required for chat deployment

Both services share **MongoDB** as the data layer.

```
┌─────────────────────────────────────────────────────┐
│           Frontend (React + Vite)                   │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
           │                          │ (Optional)
           ▼                          ▼
    ┌─────────────┐           ┌──────────────┐
    │ Main Chat   │           │   Training   │
    │ Service     │           │   Service    │
    │ (port 8000) │           │ (port 8001)  │
    └──────┬──────┘           └──────┬───────┘
           │                         │
           └────────────┬────────────┘
                        ▼
                  ┌──────────────┐
                  │  MongoDB     │
                  │  (shared db) │
                  └──────────────┘
```

## Benefits of This Architecture

✅ **Chat deployment is independent** - No training required
✅ **Training can run separately** - Async, non-blocking
✅ **Shared data layer** - Chat queries docs ingested by training
✅ **Scalability** - Each service can be scaled independently
✅ **Maintainability** - Clear separation of concerns

## Running Both Services

### Terminal 1: Start Chat Service (Main Deployment)

```bash
cd Backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create `Backend/.env` with required vars (see `.env.example`).

```bash
# Run chat service on port 8000
uvicorn main:app --reload
```

Chat API: `http://127.0.0.1:8000`
Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Start Training Service (Optional)

```bash
cd Backend
# Activate same venv as above

# Run training service on port 8001
uvicorn training_service:training_app --port 8001 --reload
```

Training API: `http://127.0.0.1:8001`
Docs: `http://127.0.0.1:8001/docs`

Or run training script directly:

```bash
python training_service.py
```

## Production Deployment

### Chat Service Only (Recommended)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

For production, **only the chat service is necessary**. Training is optional and can be:
- Run on a schedule via cron jobs
- Triggered manually via the training service
- Run in a separate container/pod

### Training Service (Optional)

```bash
uvicorn training_service:training_app --host 0.0.0.0 --port 8001
```

## Health Checks

Check if chat service is running:
```bash
curl http://127.0.0.1:8000/health
```

Check if training service is running:
```bash
curl http://127.0.0.1:8001/health
```

## API Endpoints Summary

### Chat Service (main:app on port 8000)

- `GET /chat/?q=<query>` - Ask legal question, get response with history
- `GET /chat/history` - Retrieve chat history for token
- `GET /search/?q=<query>&top_k=5&mode=auto` - Search indexed legal content
- `GET /health` - Service health check

### Training Service (training_service:training_app on port 8001)

- `POST /train/` - Start training pipeline
- `GET /health` - Service health check

## Frontend Configuration

The frontend only needs to know about the **chat service** URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Training is an **internal operation** and not exposed to the frontend in the normal flow.

## History Dependency

Chat history is fully supported and independent of training:

- Each user is issued a JWT token
- History is stored in MongoDB sessions collection
- Training doesn't affect ongoing chat sessions
- Chat works fine even if training has never run

## Notes

- Both services require MongoDB to be running
- Ensure MongoDB connection string is correct in `.env`
- Training can be resource-intensive; consider running on separate machine
- Chat service is lightweight and fast; ideal for production
