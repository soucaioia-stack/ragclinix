from app.clients import openai
from app.config import settings
from app.prompts import SYSTEM_PROMPT


def generate_response(question: str, chunks: list[str], history: list[dict]) -> str:
    """
    Monta o prompt e chama o GPT.
    - system: instruções + chunks recuperados do Qdrant
    - history: últimas mensagens da conversa (contexto)
    - user: pergunta atual
    """
    chunks_text = (
        "\n\n---\n\n".join(chunks)
        if chunks
        else "Nenhum documento relevante encontrado."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(chunks=chunks_text)},
        *history,
        {"role": "user", "content": question},
    ]

    response = openai.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=512,
    )

    return response.choices[0].message.content
