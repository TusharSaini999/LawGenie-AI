from fastapi import APIRouter
from core.train_data import main as train_main

router = APIRouter()

@router.post("/")
def train_data():
    try:
        result = train_main()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
