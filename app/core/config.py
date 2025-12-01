import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    openai_api_key: str
    law_api_key: str
    hf_token: str

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "scam_cases"

    embedding_model: str = "nlpai-lab/KURE"
    embedding_dimension: int = 1024
    similarity_threshold: float = 0.75

    model_config = SettingsConfigDict(
        env_file=".env.local" if os.path.exists(".env.local") else ".env"
    )


settings = Settings()
