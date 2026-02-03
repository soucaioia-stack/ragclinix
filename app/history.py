import json

from app.clients import redis_client
from app.config import settings


def _key(contact_id: str) -> str:
    """Key do Redis para um contato específico."""
    return f"chat:{contact_id}"


def get_history(contact_id: str) -> list[dict]:
    """Retorna o histórico completo do contato."""
    data = redis_client.get(_key(contact_id))
    return json.loads(data) if data else []


def get_recent_history(contact_id: str) -> list[dict]:
    """Retorna as últimas MAX_HISTORY mensagens para enviar ao LLM."""
    history = get_history(contact_id)
    return history[-settings.MAX_HISTORY:]


def append_messages(contact_id: str, user_msg: str, assistant_msg: str):
    """Adiciona um par user/assistant ao histórico e salva no Redis."""
    history = get_history(contact_id)
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": assistant_msg})
    redis_client.set(_key(contact_id), json.dumps(history, ensure_ascii=False))


def clear_history(contact_id: str):
    """Apaga o histórico de um contato."""
    redis_client.delete(_key(contact_id))
