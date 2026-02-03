from qdrant_client import QdrantClient
from qdrant_client.models import NamedVector
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
    Busca vetorial densa simples (Qdrant >=1.16).
    Retorna lista de textos (chunks).
    """

    # embedding → list[float]
    vector = list(embedder.embed(query))[0].tolist()

    results = client.search_points(
        collection_name=COLLECTION_NAME,
        vector=NamedVector(
            name="vectorix",   # 🔴 TEM QUE BATER COM O QDRANT
            vector=vector,
        ),
        limit=limit,
    )

    chunks = []
    for point in results.points:
        if point.payload and "text" in point.payload:
            chunks.append(point.payload["text"])

    return chunks
