from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4.1-mini"
    DENSE_MODEL: str = "text-embedding-3-small"

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    COLLECTION_NAME: str  # <-- ESSENCIAL

    # Redis
    REDIS_URL: str

    # Segurança
    INDEX_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
