from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    SparseVector,
    NamedVector,
    Fusion,
)
from fastembed import TextEmbedding
import os

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "fonte-geral")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    check_compatibility=False,
)

embedder = TextEmbedding("BAAI/bge-small-en-v1.5")


def search(query: str, limit: int = 5) -> list[str]:
    # Dense embedding → LIST[float]
    dense_vector = list(embedder.embed(query))[0].tolist()

    sparse_vector = SparseVector(indices=[], values=[])

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=NamedVector(
                    name="vectorix",          # 🔴 TEM QUE BATER COM O QDRANT
                    vector=dense_vector,
                ),
                limit=limit,
            ),
            Prefetch(
                query=NamedVector(
                    name="vectorixsparse",   # 🔴 TEM QUE BATER COM O QDRANT
                    vector=sparse_vector,
                ),
                limit=limit,
            ),
        ],
        fusion=Fusion.RRF,
        limit=limit,
    )

    chunks = []
    for point in result.points:
        if point.payload and "text" in point.payload:
            chunks.append(point.payload["text"])

    return chunks
