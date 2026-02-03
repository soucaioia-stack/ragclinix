from qdrant_client.models import Fusion, PrefetchQuery, SparseVector

from app.clients import get_sparse_model, openai, qdrant
from app.config import settings


def search(query: str, top_k: int = None) -> list[str]:
    """
    Busca híbrida no Qdrant.
    Combina dense (semântico) + sparse (keyword) com Reciprocal Rank Fusion.
    Retorna os textos dos chunks mais relevantes.
    """
    if top_k is None:
        top_k = settings.TOP_K

    # Se a collection não existe ainda (antes de indexar), retorna vazio
    if not qdrant.collection_exists(settings.COLLECTION_NAME):
        return []

    # 1. Dense embedding da pergunta (OpenAI)
    dense_response = openai.embeddings.create(model=settings.DENSE_MODEL, input=[query])
    dense_vector = dense_response.data[0].embedding

    # 2. Sparse embedding da pergunta (BM42)
    sparse_model = get_sparse_model()
    sparse_embedding = list(sparse_model.embed_documents([query]))[0]
    sparse_vector = SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist(),
    )

    # 3. Hybrid search com RRF
    #    prefetch busca os top N de cada tipo separadamente
    #    query=Fusion.RRF combina os resultados com Reciprocal Rank Fusion
    results = qdrant.query_points(
        collection_name=settings.COLLECTION_NAME,
        prefetch=[
            PrefetchQuery(query=dense_vector, using="dense", limit=top_k * 2),
            PrefetchQuery(query=sparse_vector, using="sparse", limit=top_k * 2),
        ],
        query=Fusion.RRF,
        limit=top_k,
        with_payload=True,
    )

    return [point.payload["text"] for point in results.points]
