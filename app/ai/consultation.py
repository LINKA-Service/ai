from openai import OpenAI

from app.ai.prompts.loader import prompts
from app.core.config import settings

client = OpenAI(
    api_key=settings.openai_api_key,
)


def generate_consultation_response(
    case_statement: str,
    case_type: str,
    conversation_history: list[dict],
    user_question: str,
) -> str:
    messages = [
        {"role": "system", "content": prompts.consultation_advisor},
        {
            "role": "user",
            "content": f"사건 유형: {case_type}\n사건 내용: {case_statement}",
        },
    ]

    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
