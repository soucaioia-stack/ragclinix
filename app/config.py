from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ───────────────────────────────
    # OpenAI
    # ───────────────────────────────
    OPENAI_API_KEY: str

    # Modelos
    LLM_MODEL: str = "gpt-4o-mini"
    DENSE_MODEL: str = "text-embedding-3-small"

    # ───────────────────────────────
    # Qdrant
    # ───────────────────────────────
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "fonte-geral"

    # ───────────────────────────────
    # Redis (histórico)
    # ───────────────────────────────
    REDIS_URL: str

    # Quantas mensagens anteriores entram no prompt
    MAX_HISTORY: int = 6

    # ───────────────────────────────
    # Segurança
    # ───────────────────────────────
    INDEX_TOKEN: str

    # ───────────────────────────────
    # Pydantic / Env
    # ───────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
