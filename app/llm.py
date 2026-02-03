from app.clients import openai
from app.config import settings
from app.prompts import SYSTEM_PROMPT


def generate_response(question: str, chunks: list[str], history: list[dict]) -> dict:
    """
    Monta o prompt e chama o LLM.

    Retorna:
      {
        "answer": str,
        "usage": {
            "prompt_tokens": int,
            "completion_tokens": int,
            "total_tokens": int,
            "model": str
        }
      }
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

    answer = response.choices[0].message.content
    usage = response.usage

    return {
        "answer": answer,
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "model": settings.LLM_MODEL,
        },
    }
