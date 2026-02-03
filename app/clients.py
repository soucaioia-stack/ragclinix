from qdrant_client import QdrantClient
from openai import OpenAI
from redis import Redis
from fastembed import SparseTextEmbedding

from app.config import settings

openai = OpenAI(api_key=settings.OPENAI_API_KEY)

qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=30,
)

redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)

_sparse_model = None

def get_sparse_model():
    global _sparse_model
    if _sparse_model is None:
        _sparse_model = SparseTextEmbedding("bm25")
    return _sparse_model
