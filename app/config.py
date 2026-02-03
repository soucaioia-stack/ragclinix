from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "fonte-geral"

    REDIS_URL: str
    INDEX_TOKEN: str

    DENSE_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4.1-mini"

settings = Settings()
