from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Construction Safety Support Assistant"
    debug: bool = Field(default=False)

    # Model serving
    model_server_url: str = Field(
        default="http://localhost:8001/v1/chat",
        description="vLLM HTTP endpoint for generation",
    )
    model_name: str = Field(default="Qwen2.5-3B-Instruct")

    # Embeddings
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")

    # Vector store
    vector_store: str = Field(default="faiss", description="faiss or chroma")
    vector_store_path: str = Field(default="storage/faiss.index")
    chroma_path: str = Field(default="storage/chroma_db")

    # Logging DB (not fully wired yet)
    log_db_path: str = Field(default="storage/logs.sqlite")

    # Safety
    crisis_keywords: str = Field(
        default="suicide,self-harm,kill myself,kill him,kill her,shoot,stab,"
        "jump off,hang myself,overdose,violent,assault,abuse,domestic violence",
        description="Comma-separated lexicon for quick crisis detection",
    )

    # RunPod GPU control
    runpod_api_base: str = Field(
        default="https://api.runpod.io/v2", description="RunPod API base URL"
    )
    runpod_api_key: str | None = Field(
        default=None, description="RunPod API key for GPU pod control"
    )
    runpod_pod_id: str | None = Field(
        default=None,
        description="Existing RunPod pod ID to start/stop (Option A: best)",
    )
    runpod_idle_timeout_minutes: int = Field(
        default=30,
        description="Auto-stop timeout after GPU activation if not manually stopped",
    )

    class Config:
        env_prefix = "CW_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

