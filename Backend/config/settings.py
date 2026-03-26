import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load .env file
load_dotenv()


class Settings(BaseSettings):

    # ================= Groq API =================
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field("meta-llama/llama-4-scout-17b-16e-instruct", env="GROQ_MODEL")
    groq_fallback_model: str = Field("openai/gpt-oss-120b", env="GROQ_FALLBACK_MODEL")
    groq_max_completion_tokens: int = Field(1200, env="GROQ_MAX_COMPLETION_TOKENS")
    groq_reasoning_effort: str = Field("low", env="GROQ_REASONING_EFFORT")
    
    # ================= JWT ====================
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algo: str = Field("HS256", env="JWT_ALGO")

    # ================= MongoDB ==================
    mongodb_uri: str = Field(
        default_factory=lambda: os.getenv("MONGODB_URI")
        or os.getenv("MONGO_URI")
        or "mongodb://localhost:27017"
    )
    mongodb_db_name: str = Field(
        default_factory=lambda: os.getenv("MONGODB_DB_NAME")
        or os.getenv("MONGO_DB_NAME")
        or "lawgenie"
    )
    mongo_documents_collection: str = Field("documents", env="MONGO_DOCUMENTS_COLLECTION")
    mongo_sessions_collection: str = Field("chat_sessions", env="MONGO_SESSIONS_COLLECTION")
    mongo_messages_collection: str = Field("chat_messages", env="MONGO_MESSAGES_COLLECTION")
    mongo_training_state_collection: str = Field("training_state", env="MONGO_TRAINING_STATE_COLLECTION")
    mongo_use_atlas_vector_search: bool = Field(True, env="MONGO_USE_ATLAS_VECTOR_SEARCH")
    mongo_vector_index_name: str = Field("law_chunks_vector_idx", env="MONGO_VECTOR_INDEX_NAME")
    mongo_search_index_name: str = Field("law_chunks_search_idx", env="MONGO_SEARCH_INDEX_NAME")
    mongo_embedding_dimensions: int = Field(384, env="MONGO_EMBEDDING_DIMENSIONS")
    mongo_vector_num_candidates: int = Field(120, env="MONGO_VECTOR_NUM_CANDIDATES")

    # ================= Chat Performance ==================
    chat_top_k: int = Field(3, env="CHAT_TOP_K")
    chat_max_history_turns: int = Field(6, env="CHAT_MAX_HISTORY_TURNS")
    chat_enable_browser_search: bool = Field(False, env="CHAT_ENABLE_BROWSER_SEARCH")

    chat_expiry_time: int = Field(86400, env="CHAT_EXPIRY_TIME")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Initialize settings
settings = Settings()
