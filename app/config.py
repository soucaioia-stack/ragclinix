from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str
    REDIS_URL: str

    INDEX_TOKEN: str
    LLM_MODEL: str = "gpt-4o-mini"
    DENSE_MODEL: str = "text-embedding-3-small"

settings = Settings()
