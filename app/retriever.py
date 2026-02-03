from qdrant_client.models import SparseVector, Fusion
from app.clients import qdrant, get_sparse_model, openai
from app.config import settings


def search(query: str, limit: int = 5) -> list[str]:
    dense = openai.embeddings.create(
        model=settings.DENSE_MODEL,
        input=query,
    ).data[0].embedding

    sparse_model = get_sparse_model()
    sparse = list(sparse_model.embed(query))[0]

    results = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        prefetch=[
            {
                "query": dense,
                "using": "vectorix",
                "limit": limit,
            },
            {
                "query": SparseVector(
                    indices=sparse.indices.tolist(),
                    values=sparse.values.tolist(),
                ),
                "using": "vectorixsparse",
                "limit": limit,
            },
        ],
        fusion=Fusion.RRF,
        limit=limit,
        with_payload=True,
    ).points

    return [r.payload["text"] for r in results]
