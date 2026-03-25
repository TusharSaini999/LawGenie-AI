# ============================================================
# TRAINING ROUTE - TRAINING SERVICE ONLY
# ============================================================
# This route is ONLY used by training_service.py
# NOT included in the main chat/search deployment
# ============================================================

from fastapi import APIRouter
# ============================================================
# TRAIN_DATA.PY - TRAINING ONLY MODULE
# Depends on: PyPDF2, langchain, sentence-transformers
# ============================================================
from core.train_data import main as train_main

router = APIRouter()

@router.post("/")
def train_data():
    """
    TRAINING ENDPOINT (TRAINING SERVICE ONLY)
    
    Triggers the legal document ingestion and embedding pipeline.
    This is a separate service from chat and not required for deployment.
    """
    try:
        result = train_main()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
