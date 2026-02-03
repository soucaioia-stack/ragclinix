from functools import lru_cache
import redis

from openai import OpenAI
from qdrant_client import QdrantClient
from fastembed import TextEmbedding, SparseTextEmbedding

from app.config import settings


# ─────────────────────────────────────────
# OpenAI
# ─────────────────────────────────────────
openai = OpenAI(api_key=settings.OPENAI_API_KEY)


# ─────────────────────────────────────────
# Qdrant
# ─────────────────────────────────────────
qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    check_compatibility=False,
)


# ─────────────────────────────────────────
# Redis (USANDO O n8n-redis)
# ─────────────────────────────────────────
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


# ─────────────────────────────────────────
# Embeddings
# ─────────────────────────────────────────
@lru_cache
def get_sparse_model():
    return SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2")


@lru_cache
def get_dense_model():
    return TextEmbedding("BAAI/bge-small-en-v1.5")
