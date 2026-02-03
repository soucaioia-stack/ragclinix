from qdrant_client import QdrantClient
from fastembed import TextEmbedding
import os

# ─── ENV ─────────────────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "fonte-geral")

# ─── CLIENT ──────────────────────────────────────────────────────────────────
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    check_compatibility=False,
)

# ─── EMBEDDER ────────────────────────────────────────────────────────────────
embedder = TextEmbedding("BAAI/bge-small-en-v1.5")


def search(query: str, limit: int = 5) -> list[str]:
    """
    Busca vetorial densa usando query_points (API compatível).
    """

    vector = list(embedder.embed(query))[0].tolist()

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,              # 🔴 APENAS O VECTOR
        limit=limit,
        with_payload=True,
    )

    chunks = []
    for point in result.points:
        if point.payload and "text" in point.payload:
            chunks.append(point.payload["text"])

    return chunks
