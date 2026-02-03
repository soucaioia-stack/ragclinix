from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    SparseVector,
    NamedVector,
    Fusion,
)
from fastembed import TextEmbedding
import os

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "documents")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

embedder = TextEmbedding("BAAI/bge-small-en-v1.5")


def search(query: str, limit: int = 5):
    dense_vector = list(embedder.embed(query))[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        prefetch=[
            {
                "query": dense_vector,
                "using": "dense",
                "limit": limit,
            },
            {
                "query": SparseVector(
                    indices=[],
                    values=[],
                ),
                "using": "sparse",
                "limit": limit,
            },
        ],
        fusion=Fusion.RRF,
        limit=limit,
    )

    return [
        {
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]
