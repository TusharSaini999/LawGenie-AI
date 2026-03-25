"""
Standalone Training Service for LawGenie AI

============================================
TRAINING SERVICE ONLY - NOT USED BY CHAT
============================================

This is a separate service for training the AI on legal documents.
It is independent of the main chat/search deployment.

Run this separately from the main app:
    python training_service.py

Or via uvicorn with fastapi:
    uvicorn training_service:training_app --port 8001 --reload

DEPENDENCIES:
- PyPDF2 (PDF reading)
- langchain-core, langchain-text-splitters (text splitting)
- sentence-transformers (embeddings generation)
- torch, transformers (ML models)

See requirements-training.txt for training-only dependencies.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.mongo_store import bootstrap_mongo
# ============================================
# TRAINING ROUTE - ONLY USED BY THIS SERVICE
# ============================================
from routes.train_route import router as train_router

# Create the standalone training app
training_app = FastAPI(
    title="LawGenie AI - Training Service",
    description="Standalone service for training on legal documents. Optional, not required for chat deployment.",
    version="1.0.0",
)


@training_app.on_event("startup")
def startup_event() -> None:
    """Initialize MongoDB connection on startup."""
    bootstrap_mongo()
    print("[Training Service] MongoDB initialized")


# Add CORS for training service
training_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include training routes only
training_app.include_router(train_router, prefix="/train", tags=["Training"])


@training_app.get("/health")
def health_check():
    """Check if training service is running."""
    return {
        "status": "healthy",
        "service": "training",
        "message": "Training service is running"
    }


@training_app.get("/")
def root():
    """Training service info."""
    return {
        "service": "LawGenie AI Training Service",
        "description": "Standalone service for ingesting and embedding legal documents",
        "docs_url": "/docs",
        "endpoints": {
            "train": "POST /train/",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting LawGenie AI Training Service...")
    print("Training service will be available at: http://127.0.0.1:8001")
    print("API docs: http://127.0.0.1:8001/docs")
    uvicorn.run(
        "training_service:training_app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
