from openai import OpenAI

from app.ai.legal_search import LegalSearchService
from app.ai.prompts.loader import prompts
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)
legal_search = LegalSearchService()


def _extract_search_keywords(case_type: str, statement: str, question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "당신은 법률 검색 키워드를 추출하는 전문가입니다. 주어진 사건과 질문에서 법률 검색에 필요한 핵심 키워드만 간단히 추출하세요.",
        },
        {
            "role": "user",
            "content": f"사건 유형: {case_type}\n사건 내용: {statement}\n질문: {question}\n\n위 내용에서 법률/판례 검색에 필요한 핵심 키워드 1-3개만 추출하세요. (예: 사기, 임대차, 명예훼손)",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, max_tokens=50, temperature=0.3
    )

    return response.choices[0].message.content.strip()


def _format_legal_references(legal_data: dict) -> str:
    if not legal_data["precedents"] and not legal_data["laws"]:
        return ""

    parts = ["\n\n=== 관련 법률 자료 ===\n"]

    if legal_data["precedents"]:
        parts.append("\n【판례】")
        for i, prec in enumerate(legal_data["precedents"], 1):
            parts.append(
                f"\n{i}. {prec['title']}"
                f"\n   사건번호: {prec['case_number']}"
                f"\n   법원: {prec['court']} ({prec['date']})"
                f"\n   요약: {prec['summary']}"
            )

    if legal_data["laws"]:
        parts.append("\n\n【관련 법령】")
        for i, law in enumerate(legal_data["laws"], 1):
            parts.append(
                f"\n{i}. {law['title']}"
                f"\n   시행일: {law['enforcement_date']}"
                f"\n   내용: {law['content']}"
            )

    return "".join(parts)


def generate_consultation_response(
    case_statement: str,
    case_type: str,
    conversation_history: list[dict],
    user_question: str,
    include_legal_search: bool = True,
) -> str:
    legal_context = ""

    if include_legal_search:
        keywords = _extract_search_keywords(case_type, case_statement, user_question)
        legal_data = legal_search.search_all(keywords, prec_count=2, law_count=2)
        legal_context = _format_legal_references(legal_data)

    system_prompt = prompts.consultation_advisor
    if legal_context:
        system_prompt += "\n\n아래 법률 자료를 참고하여 답변하되, 자연스럽게 통합하여 설명하세요. 출처를 명시할 필요는 없습니다."
        system_prompt += legal_context

    messages = [
        {"role": "system", "content": system_prompt},
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
        max_tokens=1500,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
