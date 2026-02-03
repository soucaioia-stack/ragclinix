import hashlib
import re
import uuid
import requests
import yaml

from qdrant_client.models import (
    PointStruct,
    SparseVector,
)

from fastembed import TextEmbedding, SparseTextEmbedding

from app.clients import qdrant
from app.config import settings


# ─────────────────────────────────────────────────────────────
# EMBEDDERS (HÍBRIDO)
# ─────────────────────────────────────────────────────────────

dense_embedder = TextEmbedding("BAAI/bge-small-en-v1.5")
sparse_embedder = SparseTextEmbedding("prithivida/Splade_PP_en_v1")


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

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
            section_name = header.replace("## ", "").strip()
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
    digest = hashlib.sha256(key.encode()).digest()
    return str(uuid.UUID(bytes=digest[:16]))


# ─────────────────────────────────────────────────────────────
# INDEXAÇÃO HÍBRIDA
# ─────────────────────────────────────────────────────────────

def index_document(url: str) -> dict:
    """
    Pipeline híbrido definitivo:
    - Dense: BGE
    - Sparse: SPLADE
    - Vetores nomeados:
        - vectorix
        - vectorixsparse
    """

    # 1. Baixar markdown
    content = fetch_md(url)

    # 2. Frontmatter + corpo
    metadata, body = parse_frontmatter(content)
    chunks = chunk_by_sections(body, metadata, url)

    if not chunks:
        return {
            "status": "erro",
            "mensagem": "Nenhum chunk gerado. Verifique o markdown.",
        }

    texts = [chunk["text"] for chunk in chunks]

    # 3. Dense embeddings
    dense_vectors = list(dense_embedder.embed(texts))

    # 4. Sparse embeddings (SPLADE)
    sparse_vectors = list(sparse_embedder.embed(texts))

    # 5. Montar pontos
    points: list[PointStruct] = []

    for i, chunk in enumerate(chunks):
        point_id = generate_point_id(url, chunk["metadata"]["section"])

        points.append(
            PointStruct(
                id=point_id,
                vector={
                    "vectorix": dense_vectors[i],
                    "vectorixsparse": SparseVector(
                        indices=sparse_vectors[i].indices,
                        values=sparse_vectors[i].values,
                    ),
                },
                payload={
                    "text": chunk["text"],
                    **chunk["metadata"],
                },
            )
        )

    # 6. Upsert
    qdrant.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
    )

    return {
        "status": "ok",
        "chunks_indexados": len(points),
        "collection": settings.QDRANT_COLLECTION,
        "source": url,
    }
