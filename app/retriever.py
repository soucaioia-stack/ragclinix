from collections import defaultdict
from qdrant_client.models import SparseVector

from app.clients import qdrant, get_sparse_model, openai
from app.config import settings


def reciprocal_rank_fusion(results_lists, k=60):
    scores = defaultdict(float)
    for results in results_lists:
        for rank, point in enumerate(results):
            scores[point.id] += 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def search(query: str, limit: int = 5) -> list[str]:
    # ── Dense embedding (OpenAI) ─────────────────
    dense_vector = openai.embeddings.create(
        model=settings.DENSE_MODEL,
        input=query,
    ).data[0].embedding

    dense_results = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=dense_vector,
        using="vectorix",
        with_payload=True,
        limit=limit * 2,
    ).points

    # ── Sparse embedding (fastembed / BM25) ──────
    sparse_model = get_sparse_model()
    sparse_embedding = list(sparse_model.embed(query))[0]

    sparse_results = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=SparseVector(
            indices=sparse_embedding.indices.tolist(),
            values=sparse_embedding.values.tolist(),
        ),
        using="vectorixsparse",
        with_payload=True,
        limit=limit * 2,
    ).points

    # ── Fusion manual ────────────────────────────
    fused = reciprocal_rank_fusion(
        [dense_results, sparse_results]
    )[:limit]

    # ── Retorna textos ───────────────────────────
    payloads = {
        p.id: p.payload for p in dense_results + sparse_results
    }

    return [
        payloads[pid]["text"]
        for pid, _ in fused
        if "text" in payloads.get(pid, {})
    ]
