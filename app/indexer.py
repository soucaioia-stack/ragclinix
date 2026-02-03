from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.clients import qdrant, openai, get_sparse_model
from app.config import settings
import requests, hashlib, uuid, re, yaml


def ensure_collection():
    if not qdrant.collection_exists(settings.QDRANT_COLLECTION):
        qdrant.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config={
                "vectorix": VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                "vectorixsparse": SparseVectorParams(),
            },
        )


def index_document(url: str):
    content = requests.get(url, timeout=30).text

    ensure_collection()

    text = content

    dense = openai.embeddings.create(
        model=settings.DENSE_MODEL,
        input=text,
    ).data[0].embedding

    sparse_model = get_sparse_model()
    sparse = list(sparse_model.embed(text))[0]

    point_id = str(uuid.uuid4())

    qdrant.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector={
                    "vectorix": dense,
                    "vectorixsparse": SparseVector(
                        indices=sparse.indices.tolist(),
                        values=sparse.values.tolist(),
                    ),
                },
                payload={
                    "text": text,
                    "source": url,
                },
            )
        ],
    )

    return {"status": "ok", "id": point_id}
