from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    DENSE_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "fonte-geral"

    # Redis
    REDIS_URL: str
    MAX_HISTORY: int = 6

    # Segurança
    INDEX_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()
