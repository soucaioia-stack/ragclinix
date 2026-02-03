from functools import lru_cache

from openai import OpenAI
from qdrant_client import QdrantClient
from fastembed import TextEmbedding, SparseTextEmbedding

from app.config import settings


# OpenAI client
openai = OpenAI(api_key=settings.OPENAI_API_KEY)


# Qdrant client
qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    check_compatibility=False,  # remove warnings inúteis
)


# Sparse model (BM42)
@lru_cache
def get_sparse_model():
    return SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2")


# Dense model (FastEmbed só p/ busca, OpenAI p/ index)
@lru_cache
def get_dense_model():
    return TextEmbedding("BAAI/bge-small-en-v1.5")
