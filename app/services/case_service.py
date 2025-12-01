from typing import List, Optional

from sqlalchemy.orm import Session

from app.ai.case import analyze_case, generate_title
from app.core.exceptions import UnprocessableEntityException
from app.models.case import Case, ScammerInfo, CaseStatus
from app.models.user import User
from app.schemas.case import CaseCreate


class CaseService:
    def __init__(self, db: Session):
        self.db = db

    def create_case(self, case: CaseCreate, user_id: int) -> Case:
        status = analyze_case(case.case_type, case.statement, case.scammer_infos):
        if status == CaseStatus.Rejected:
            raise UnprocessableEntityException("Invalid or inappropriate case content")
        case_title = generate_title(case.statement)
        db_case = Case(
            user_id=user_id,
            case_type=case.case_type,
            case_type_other=case.case_type_other,
            title=case_title,
            statement=case.statement,
            status=status
        )
        self.db.add(db_case)
        self.db.flush()

        for info in case.scammer_infos:
            scammer_info = ScammerInfo(
                case_id=db_case.id, info_type=info.info_type, value=info.value
            )
            self.db.add(scammer_info)

        self.db.commit()
        self.db.refresh(db_case)
        return db_case

    def get_user_cases(self, user_id: int) -> List[Case]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.cases

    def get_case(self, case_id: int) -> Optional[Case]:
        return self.db.query(Case).filter(Case.id == case_id).first()

    def delete_case(self, case_id: int, user_id: int) -> None:
        db_case = self.db.query(Case).filter(Case.id == case_id).first()
        if not db_case:
            raise NotFoundException("Case not found")

        if db_case.user_id != user_id:
            raise ForbiddenException("Only case owner can delete")

        self.db.delete(db_case)
        self.db.commit()
