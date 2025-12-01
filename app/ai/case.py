from openai import OpenAI

from app.ai.prompts.loader import prompts
from app.core.config import settings
from app.models.case import CaseStatus

client = OpenAI(
    api_key=settings.openai_api_key,
)


async def generate_title(statement: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompts.case_title},
            {"role": "user", "content": statement},
        ],
        max_tokens=50,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


async def analyze_case(case_type: str, statement: str, scammer_infos: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompts.case_analysis},
            {
                "role": "user",
                "content": f"statement: {statement}\nscammer_infos: {scammer_infos}\ncase_type: {case_type}",
            },
        ],
        max_tokens=50,
        temperature=0.5,
    )
    result = response.choices[0].message.content.strip()
    status_map = {
        "통과": CaseStatus.APPROVED,
        "검토": CaseStatus.PENDING,
        "거부": CaseStatus.REJECTED,
    }

    return status_map.get(result, CaseStatus.PENDING)
