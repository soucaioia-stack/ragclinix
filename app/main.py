from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.history import append_messages, clear_history, get_history, get_recent_history
from app.indexer import index_document
from app.llm import generate_response
from app.retriever import search

app = FastAPI(title="RAG Clínica")


# ─── Schemas ─────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    contact_id: str  # ex: número do WhatsApp do contato


class IndexRequest(BaseModel):
    url: str  # URL raw do arquivo .md no GitHub


# ─── Helper ──────────────────────────────────────────────────────────────────
def _check_token(authorization: str):
    """Valida o INDEX_TOKEN nos endpoints admin."""
    token = authorization.replace("Bearer ", "")
    if token != settings.INDEX_TOKEN:
        raise HTTPException(status_code=401, detail="Não autorizado")


# ─── Endpoint público ────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Liveness check — útil pro Easypanel confirmar que o container está ok."""
    return {"status": "ok"}


@app.post("/query")
def query(request: QueryRequest):
    """
    Endpoint principal — chamado pelo n8n a cada mensagem do WhatsApp.

    Fluxo:
      1. Busca histórico recente no Redis
      2. Busca híbrida no Qdrant
      3. Gera resposta com GPT
      4. Salva mensagens no histórico
      5. Retorna resposta para o n8n
    """
    try:
        history = get_recent_history(request.contact_id)
        chunks = search(request.question)
        answer = generate_response(request.question, chunks, history)
        append_messages(request.contact_id, request.question, answer)
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Endpoints admin (protegidos por INDEX_TOKEN) ────────────────────────────
@app.post("/index")
def index(request: IndexRequest, authorization: str = Header(...)):
    """
    Indexa um documento .md pelo URL raw do GitHub.
    Uso: curl com Authorization: Bearer <INDEX_TOKEN>
    """
    _check_token(authorization)
    try:
        return index_document(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{contact_id}")
def get_history_endpoint(contact_id: str, authorization: str = Header(...)):
    """Retorna histórico completo de um contato (para debug)."""
    _check_token(authorization)
    return {"history": get_history(contact_id)}


@app.delete("/history/{contact_id}")
def clear_history_endpoint(contact_id: str, authorization: str = Header(...)):
    """Apaga o histórico de um contato."""
    _check_token(authorization)
    clear_history(contact_id)
    return {"status": "ok"}
