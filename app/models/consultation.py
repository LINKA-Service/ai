from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    author = relationship("User", back_populates="consultations")
    group = relationship("Group", back_populates="consultations")
    messages = relationship(
        "ConsultationMessage",
        back_populates="consultation",
        cascade="all, delete-orphan",
    )


class ConsultationMessage(Base):
    __tablename__ = "consultation_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    consultation_id = Column(
        Integer, ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    consultation = relationship("Consultation", back_populates="messages")
    author = relationship("User", back_populates="consultation_messages")
