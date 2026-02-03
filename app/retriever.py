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
    Busca vetorial simples (dense).
    Retorna lista de chunks (textos).
    """

    # embedding → list[float]
    vector = list(embedder.embed(query))[0].tolist()

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=("vectorix", vector),  # 🔴 nome do vector no Qdrant
        limit=limit,
    )

    chunks = []
    for hit in hits:
        if hit.payload and "text" in hit.payload:
            chunks.append(hit.payload["text"])

    return chunks
