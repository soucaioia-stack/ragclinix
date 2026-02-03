from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env"}

    # OpenAI
    OPENAI_API_KEY: str

    # Qdrant Cloud
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # Redis
    REDIS_URL: str

    # App
    COLLECTION_NAME: str = "clinica_docs"
    INDEX_TOKEN: str  # protege endpoints admin
    DENSE_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4.1-mini"
    TOP_K: int = 5
    MAX_HISTORY: int = 20  # mensagens enviadas ao LLM (salva todas no Redis)


settings = Settings()
