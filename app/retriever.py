from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    SparseVector,
    Fusion,
)
from fastembed import TextEmbedding
import os

# ─── ENV VARS ────────────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "fonte-geral")

# ─── CLIENT ──────────────────────────────────────────────────────────────────
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    check_compatibility=False,  # remove warning chato
)

# ─── EMBEDDINGS ──────────────────────────────────────────────────────────────
embedder = TextEmbedding("BAAI/bge-small-en-v1.5")


# ─── SEARCH ──────────────────────────────────────────────────────────────────
def search(query: str, limit: int = 5) -> list[str]:
    """
    Busca híbrida (dense + sparse) no Qdrant
    Retorna lista de textos (chunks)
    """

    # Dense embedding
    dense_vector = list(embedder.embed(query))[0]

    # Sparse placeholder (fastembed não gera sparse automaticamente)
    sparse_vector = SparseVector(indices=[], values=[])

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                vector=dense_vector,
                using="vectorix",  # ⚠️ nome do dense vector na coleção
                limit=limit,
            ),
            Prefetch(
                vector=sparse_vector,
                using="vectorixsparse",  # ⚠️ nome do sparse vector
                limit=limit,
            ),
        ],
        fusion=Fusion.RRF,
        limit=limit,
    )

    # Extrai apenas o texto do payload
    chunks = []
    for point in result.points:
        if point.payload and "text" in point.payload:
            chunks.append(point.payload["text"])

    return chunks
