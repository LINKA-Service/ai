from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from app.models.case import Case
from app.models.consultation import Consultation, ConsultationMessage
from app.models.group import Group
from app.models.user import User
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationMessageCreate,
)


class ConsultationService:
    def __init__(self, db: Session):
        self.db = db

    def create_consultation(
        self, consultation: ConsultationCreate, user_id: int
    ) -> Consultation:
        case = self.db.query(Case).filter(Case.id == consultation.case_id).first()
        if not case:
            raise NotFoundException("Case not found")

        if case.user_id != user_id:
            raise ForbiddenException("Only case owner can create consultation")

        if consultation.group_id:
            group = (
                self.db.query(Group).filter(Group.id == consultation.group_id).first()
            )
            if not group:
                raise NotFoundException("Group not found")

            user = self.db.query(User).filter(User.id == user_id).first()
            if user not in group.members and group.owner_id != user_id:
                raise ForbiddenException(
                    "Must be a group member to create consultation in this group"
                )

        db_consultation = Consultation(
            case_id=consultation.case_id,
            name=consultation.name,
            author_id=user_id,
            group_id=consultation.group_id,
        )
        self.db.add(db_consultation)
        self.db.commit()
        self.db.refresh(db_consultation)
        return db_consultation

    def get_user_consultations(self, user_id: int) -> List[Consultation]:
        return (
            self.db.query(Consultation)
            .filter(Consultation.author_id == user_id)
            .order_by(Consultation.created_at.desc())
            .all()
        )

    def get_group_consultations(
        self, group_id: int, user_id: int
    ) -> List[Consultation]:
        group = self.db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise NotFoundException("Group not found")

        user = self.db.query(User).filter(User.id == user_id).first()
        if user not in group.members and group.owner_id != user_id:
            raise ForbiddenException("Must be a group member to view consultations")

        return (
            self.db.query(Consultation)
            .filter(Consultation.group_id == group_id)
            .order_by(Consultation.created_at.desc())
            .all()
        )

    def get_consultation(self, consultation_id: int) -> Optional[Consultation]:
        return (
            self.db.query(Consultation)
            .filter(Consultation.id == consultation_id)
            .first()
        )

    def can_access_consultation(self, consultation_id: int, user_id: int) -> bool:
        consultation = self.get_consultation(consultation_id)
        if not consultation:
            return False

        if consultation.author_id == user_id:
            return True

        if consultation.group_id:
            group = (
                self.db.query(Group).filter(Group.id == consultation.group_id).first()
            )
            if group:
                user = self.db.query(User).filter(User.id == user_id).first()
                return user in group.members or group.owner_id == user_id

        return False

    def delete_consultation(self, consultation_id: int, user_id: int) -> None:
        db_consultation = (
            self.db.query(Consultation)
            .filter(Consultation.id == consultation_id)
            .first()
        )
        if not db_consultation:
            raise NotFoundException("Consultation not found")

        if db_consultation.author_id != user_id:
            raise ForbiddenException("Only consultation owner can delete")

        self.db.delete(db_consultation)
        self.db.commit()

    def create_message(
        self, consultation_id: int, message: ConsultationMessageCreate, user_id: int
    ) -> ConsultationMessage:
        consultation = (
            self.db.query(Consultation)
            .filter(Consultation.id == consultation_id)
            .first()
        )
        if not consultation:
            raise NotFoundException("Consultation not found")

        if not self.can_access_consultation(consultation_id, user_id):
            raise ForbiddenException("Access denied")

        db_message = ConsultationMessage(
            content=message.content,
            consultation_id=consultation_id,
            author_id=user_id,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_consultation_messages(
        self, consultation_id: int, skip: int = 0, limit: int = 50
    ) -> List[ConsultationMessage]:
        return (
            self.db.query(ConsultationMessage)
            .filter(ConsultationMessage.consultation_id == consultation_id)
            .order_by(ConsultationMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_message(self, message_id: int, user_id: int) -> None:
        db_message = (
            self.db.query(ConsultationMessage)
            .filter(ConsultationMessage.id == message_id)
            .first()
        )
        if not db_message:
            raise NotFoundException("Message not found")

        if db_message.author_id != user_id:
            raise ForbiddenException("Can only delete own messages")

        self.db.delete(db_message)
        self.db.commit()
