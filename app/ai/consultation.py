from openai import OpenAI

from app.ai.legal_search import LegalRepository
from app.ai.prompts.loader import prompts
from app.core.config import settings


class ConsultationService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.legal_search = LegalRepository()

    def _generate_keywords(self, case_type: str, statement: str, question: str) -> str:
        messages = [
            {"role": "system", "content": prompts.consultation_keyword},
            {
                "role": "user",
                "content": f"사건 유형: {case_type}\n사건 내용: {statement}\n질문: {question}",
            },
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, max_tokens=50, temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def _format_references(self, legal_data: dict) -> str:
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

    def generate_response(
        self,
        case_statement: str,
        case_type: str,
        conversation_history: list[dict],
        user_question: str,
        include_legal_search: bool = True,
    ) -> str:
        legal_context = ""

        if include_legal_search:
            keywords = self._generate_keywords(case_type, case_statement, user_question)
            legal_data = self.legal_search.search_all(
                keywords, prec_count=2, law_count=2
            )
            legal_context = self._format_references(legal_data)

        system_prompt = prompts.consultation_answer
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

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
