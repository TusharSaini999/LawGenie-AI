from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.mongo_store import bootstrap_mongo
from routes.chat_route import router as chat_router
from routes.search_route import router as search_router

# ====================================================
# CHAT AND SEARCH DEPLOYMENT SERVICE
# ====================================================
# This is the main deployment app for chat and search.
# Training is handled by the separate training_service.py
# See training_service.py for how to run training separately.
# ====================================================

app = FastAPI(
    title="LawGenie AI Backend",
    description="Deployment-ready chat and search service. For training, use training_service.py",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event() -> None:
    """Initialize MongoDB connection on startup."""
    bootstrap_mongo()
    print("[Chat Service] MongoDB initialized")


# Add CORS Middleware
# This allows the frontend to make requests to this backend
app.add_middleware(
    CORSMiddleware,
    # List of origins that are allowed to make requests
    # Include active frontend dev ports and common local hosts.
    allow_origins=[
        "http://localhost:5178",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,     # Allow cookies/auth headers
    # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    allow_headers=["*"],        # Allow all headers
)

# Include Routes: Chat and Search only (no training)
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(search_router, prefix="/search", tags=["Search"])


@app.get("/health")
def health_check():
    """Check if the chat service is running."""
    return {
        "status": "healthy",
        "service": "chat",
        "message": "Chat and search service is running"
    }


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs
