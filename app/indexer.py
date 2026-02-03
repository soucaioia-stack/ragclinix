import hashlib
import re
import uuid

import requests
import yaml
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.clients import get_sparse_model, openai, qdrant
from app.config import settings


def fetch_md(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_frontmatter(content: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if match:
        metadata = yaml.safe_load(match.group(1)) or {}
        body = match.group(2)
        return metadata, body
    return {}, content


def chunk_by_sections(body: str, metadata: dict, source_url: str) -> list[dict]:
    parts = re.split(r"^(##\s+.+)$", body, flags=re.MULTILINE)

    chunks = []
    i = 1
    while i < len(parts) - 1:
        header = parts[i].strip()
        content = parts[i + 1].strip()
        if content:
            section_name = header.replace("## ", "")
            chunks.append(
                {
                    "text": f"{header}\n{content}",
                    "metadata": {
                        "tipo": metadata.get("tipo", "unknown"),
                        "nome": metadata.get("nome", "unknown"),
                        "section": section_name,
                        "source_url": source_url,
                    },
                }
            )
        i += 2

    return chunks


def generate_point_id(source_url: str, section: str) -> str:
    key = f"{source_url}:{section}"
    hash_bytes = hashlib.sha256(key.encode()).digest()
    return str(uuid.UUID(bytes=hash_bytes[:16]))


def ensure_collection():
    if not qdrant.collection_exists(settings.COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(),
            },
        )


def index_document(url: str) -> dict:
    content = fetch_md(url)
    metadata, body = parse_frontmatter(content)
    chunks = chunk_by_sections(body, metadata, url)

    if not chunks:
        return {"status": "erro", "mensagem": "Nenhum chunk gerado"}

    ensure_collection()

    texts = [chunk["text"] for chunk in chunks]

    # Dense (OpenAI)
    dense_response = openai.embeddings.create(
        model=settings.DENSE_MODEL,
        input=texts,
    )
    dense_vectors = [item.embedding for item in dense_response.data]

    # Sparse (BM25)
    sparse_model = get_sparse_model()
    sparse_embeddings = list(sparse_model.embed(texts))

    points = []
    for i, chunk in enumerate(chunks):
        point_id = generate_point_id(url, chunk["metadata"]["section"])

        points.append(
            PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vectors[i],
                    "sparse": SparseVector(
                        indices=sparse_embeddings[i].indices.tolist(),
                        values=sparse_embeddings[i].values.tolist(),
                    ),
                },
                payload={
                    "text": chunk["text"],
                    **chunk["metadata"],
                },
            )
        )

    qdrant.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=points,
    )

    return {
        "status": "ok",
        "chunks_indexados": len(points),
        "source": url,
    }
