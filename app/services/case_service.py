from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.ai.case import analyze_case, generate_title
from app.ai.vector_store import VectorStore
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnprocessableEntityException,
)
from app.models.case import Case, CaseStatus, ScammerInfo
from app.schemas.case import CaseCreate


def to_db_value(enum_val):
    if hasattr(enum_val, "value"):
        return enum_val.value
    if isinstance(enum_val, str):
        return enum_val.lower()
    return str(enum_val).lower()


class CaseService:
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore()

    async def create_case(self, case: CaseCreate, user_id: int) -> Case:
        status = await analyze_case(case.case_type, case.statement, case.scammer_infos)
        if status == CaseStatus.REJECTED:
            raise UnprocessableEntityException("Invalid or inappropriate case content")

        case_title = await generate_title(case.statement)

        case_type_value = to_db_value(case.case_type)
        status_value = to_db_value(status)

        db_case = Case(
            user_id=user_id,
            case_type=case_type_value,
            case_type_other=case.case_type_other,
            title=case_title,
            statement=case.statement,
            status=status_value,
        )

        self.db.add(db_case)
        self.db.flush()

    def get_user_cases(self, user_id: int) -> List[Case]:
        return (
            self.db.query(Case)
            .options(joinedload(Case.scammer_infos))
            .filter(Case.user_id == user_id)
            .all()
        )

    def get_user_case(self, case_id: int, user_id: int) -> Case:
        case = (
            self.db.query(Case)
            .options(joinedload(Case.scammer_infos))
            .filter(Case.id == case_id)
            .first()
        )
        if not case:
            raise NotFoundException("Case not found")
        if case.user_id != user_id:
            raise ForbiddenException("Access denied")
        return case

    def get_case(self, case_id: int) -> Optional[Case]:
        return (
            self.db.query(Case)
            .options(joinedload(Case.scammer_infos))
            .filter(Case.id == case_id)
            .first()
        )

    def delete_case(self, case_id: int, user_id: int) -> None:
        db_case = self.db.query(Case).filter(Case.id == case_id).first()
        if not db_case:
            raise NotFoundException("Case not found")

        if db_case.user_id != user_id:
            raise ForbiddenException("Only case owner can delete")

        self.vector_store.delete_case(case_id)
        self.db.delete(db_case)
        self.db.commit()

    def get_similar_cases(
        self, case_id: int, user_id: int, limit: int = 5
    ) -> List[dict]:
        case = self.get_user_case(case_id, user_id)
        return self.vector_store.search_by_case(case, limit=limit)
