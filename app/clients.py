from openai import OpenAI
from qdrant_client import QdrantClient
from fastembed import SparseTextEmbedding
import redis
from app.config import settings

# ── OpenAI ─────────────────────────────────────
openai = OpenAI(api_key=settings.OPENAI_API_KEY)

# ── Qdrant ─────────────────────────────────────
qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# ── Redis ──────────────────────────────────────
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)

# ── Sparse model (BM25-like) ───────────────────
_sparse_model = None


def get_sparse_model():
    global _sparse_model
    if _sparse_model is None:
        _sparse_model = SparseTextEmbedding("Qdrant/bm25")
    return _sparse_model
