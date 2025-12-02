from typing import Dict, List

import requests

from app.core.config import settings


class LegalRepository:
    def __init__(self):
        self.base_url = "https://www.law.go.kr/DRF/lawSearch.do"
        self.api_key = settings.law_api_key

    def search_precedents(self, query: str, display: int = 5) -> List[Dict]:
        params = {
            "OC": self.api_key,
            "target": "prec",
            "type": "JSON",
            "query": query,
            "display": display,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            precedents = []
            prec_list = data.get("PrecSearch", [{}])[0].get("prec", [])

            for prec in prec_list:
                precedents.append(
                    {
                        "title": prec.get("판례명칭", ""),
                        "case_number": prec.get("사건번호", ""),
                        "court": prec.get("법원명", ""),
                        "date": prec.get("선고일자", ""),
                        "summary": prec.get("판례내용", "")[:500],
                        "type": "precedent",
                    }
                )

            return precedents
        except:
            return []

    def search_laws(self, query: str, display: int = 5) -> List[Dict]:
        params = {
            "OC": self.api_key,
            "target": "law",
            "type": "JSON",
            "query": query,
            "display": display,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            laws = []
            law_list = data.get("LawSearch", [{}])[0].get("law", [])

            for law in law_list:
                laws.append(
                    {
                        "title": law.get("법령명한글", ""),
                        "law_id": law.get("법령ID", ""),
                        "enforcement_date": law.get("시행일자", ""),
                        "content": law.get("법령내용", "")[:500],
                        "type": "law",
                    }
                )

            return laws
        except:
            return []

    def search_all(
        self, query: str, prec_count: int = 3, law_count: int = 3
    ) -> Dict[str, List[Dict]]:
        return {
            "precedents": self.search_precedents(query, prec_count),
            "laws": self.search_laws(query, law_count),
        }
