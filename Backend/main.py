from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Import this
from core.mongo_store import bootstrap_mongo
from routes.chat_route import router as chat_router
from routes.search_route import router as search_router
from routes.train_route import router as train_router

# Start the App
app = FastAPI(title="AI Bot Backend")


@app.on_event("startup")
def startup_event() -> None:
    bootstrap_mongo()


# 2. Add CORS Middleware
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

# Include Routes
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(train_router, prefix="/train", tags=["Training"])

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs
