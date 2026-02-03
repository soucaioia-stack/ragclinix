from openai import OpenAI
from qdrant_client import QdrantClient
import redis

from app.config import settings

# Clientes globais (uma instância só, reutilizada)
openai = OpenAI(api_key=settings.OPENAI_API_KEY)

qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# Modelo sparse com lazy init
# Baixa o modelo BM42 na primeira chamada e caches afterwards
_sparse_model = None


def get_sparse_model():
    global _sparse_model
    if _sparse_model is None:
        from fastembed import SparseTextEmbedding

        _sparse_model = SparseTextEmbedding(model_name="Qdrant/bm42-all-MiniLM-L6-v2-onnx")
    return _sparse_model
