import hashlib
from datetime import datetime
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.ai.embedding_engine import EmbeddingEngine
from app.core.config import settings
from app.models.case import Case


class VectorStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection
        self.embedding_service = EmbeddingEngine()
        self._ensure_collection()
        self._initialized = True

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension, distance=Distance.COSINE
                ),
            )

    def _create_search_text(self, case: Case) -> str:
        case_type_map = {
            "delivery": "직거래",
            "insurance": "보험",
            "door_to_door": "방문판매",
            "appointment": "사칭",
            "rental": "전세",
            "romance": "로맨스스캠",
            "smishing": "스미싱",
            "false_advertising": "허위광고",
            "secondhand_fraud": "중고거래",
            "investment_scam": "투자",
            "account_takeover": "계정도용",
            "other": "기타",
        }

        parts = [
            f"유형: {case_type_map.get(case.case_type.value, case.case_type.value)}",
            f"제목: {case.title}",
            f"내용: {case.statement}",
        ]

        if case.case_type_other:
            parts.insert(1, f"세부유형: {case.case_type_other}")

        if case.scammer_infos:
            info_texts = []
            info_type_map = {
                "name": "이름",
                "nickname": "닉네임",
                "phone": "전화",
                "account": "계좌",
                "sns_id": "SNS",
            }
            for info in case.scammer_infos:
                info_type = info_type_map.get(
                    info.info_type.value, info.info_type.value
                )
                info_texts.append(f"{info_type}:{info.value}")
            parts.append(f"정보: {', '.join(info_texts)}")

        return "\n".join(parts)

    def _generate_point_id(self, case_id: int) -> str:
        return hashlib.md5(f"case_{case_id}".encode()).hexdigest()

    def index_case(self, case: Case) -> bool:
        try:
            search_text = self._create_search_text(case)
            embedding = self.embedding_service.encode_document(search_text)

            scammer_infos_data = []
            if case.scammer_infos:
                for info in case.scammer_infos:
                    scammer_infos_data.append(
                        {"info_type": info.info_type.value, "value": info.value}
                    )

            payload = {
                "case_id": case.id,
                "case_type": case.case_type.value,
                "title": case.title,
                "statement": case.statement[:500],
                "status": case.status.value,
                "created_at": case.created_at.isoformat() if case.created_at else None,
                "scammer_infos": scammer_infos_data,
                "indexed_at": datetime.utcnow().isoformat(),
            }

            point_id = self._generate_point_id(case.id)

            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(id=point_id, vector=embedding, payload=payload)],
            )

            return True
        except Exception as e:
            print(f"Error indexing case {case.id}: {e}")
            return False

    def search_similar(
        self,
        query_text: str,
        case_type: Optional[str] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        exclude_case_id: Optional[int] = None,
    ) -> List[Dict]:
        try:
            if score_threshold is None:
                score_threshold = settings.similarity_threshold

            query_embedding = self.embedding_service.encode_query(query_text)

            must_conditions = [
                FieldCondition(key="status", match=MatchValue(value="approved"))
            ]

            if case_type:
                must_conditions.append(
                    FieldCondition(key="case_type", match=MatchValue(value=case_type))
                )

            must_not_conditions = []
            if exclude_case_id:
                must_not_conditions.append(
                    FieldCondition(
                        key="case_id", match=MatchValue(value=exclude_case_id)
                    )
                )

            search_filter = Filter(
                must=must_conditions,
                must_not=must_not_conditions if must_not_conditions else None,
            )

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            similar_cases = []
            for result in results:
                similar_cases.append(
                    {
                        "case_id": result.payload["case_id"],
                        "title": result.payload["title"],
                        "case_type": result.payload["case_type"],
                        "statement": result.payload["statement"],
                        "scammer_infos": result.payload.get("scammer_infos", []),
                        "similarity_score": round(result.score, 4),
                        "created_at": result.payload.get("created_at"),
                    }
                )

            return similar_cases
        except Exception as e:
            print(f"Error searching similar cases: {e}")
            return []

    def search_by_case(
        self, case: Case, limit: int = 5, score_threshold: Optional[float] = None
    ) -> List[Dict]:
        search_text = self._create_search_text(case)
        return self.search_similar(
            query_text=search_text,
            case_type=case.case_type.value,
            limit=limit,
            score_threshold=score_threshold,
            exclude_case_id=case.id,
        )

    def delete_case(self, case_id: int) -> bool:
        try:
            point_id = self._generate_point_id(case_id)
            self.client.delete(
                collection_name=self.collection_name, points_selector=[point_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting case {case_id}: {e}")
            return False

    def update_case(self, case: Case) -> bool:
        self.delete_case(case.id)
        return self.index_case(case)
