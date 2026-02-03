from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.history import (
    append_messages,
    clear_history,
    get_history,
    get_recent_history,
)
from app.indexer import index_document
from app.llm import generate_response
from app.retriever import search

app = FastAPI(title="RAG Clínica")


# ─── Schemas ────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    contact_id: str  # ex: número do WhatsApp


class IndexRequest(BaseModel):
    url: str  # URL raw do arquivo .md


# ─── Helpers de segurança ───────────────────────────────────────────────────
def _check_index_token(authorization: str | None):
    if authorization != f"Bearer {settings.INDEX_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")


def _check_query_token(authorization: str | None):
    if authorization != f"Bearer {settings.QUERY_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")


# ─── Público ────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query(
    request: QueryRequest,
    authorization: str | None = Header(default=None),
):
    """
    Endpoint principal — chamado pelo n8n / WhatsApp.
    """
    _check_query_token(authorization)

    try:
        history = get_recent_history(request.contact_id)
        chunks = search(request.question)

        result = generate_response(
            request.question,
            chunks,
            history,
        )

        append_messages(
            request.contact_id,
            request.question,
            result["answer"],
        )

        return {
            "response": result["answer"],
            "usage": result["usage"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Admin ──────────────────────────────────────────────────────────────────
@app.post("/index")
def index(
    request: IndexRequest,
    authorization: str | None = Header(default=None),
):
    _check_index_token(authorization)
    return index_document(request.url)


@app.get("/history/{contact_id}")
def get_history_endpoint(
    contact_id: str,
    authorization: str | None = Header(default=None),
):
    _check_index_token(authorization)
    return {"history": get_history(contact_id)}


@app.delete("/history/{contact_id}")
def clear_history_endpoint(
    contact_id: str,
    authorization: str | None = Header(default=None),
):
    _check_index_token(authorization)
    clear_history(contact_id)
    return {"status": "ok"}
