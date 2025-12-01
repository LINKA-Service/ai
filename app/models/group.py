from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.lawyer import lawyer_groups
from app.models.user import user_groups


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="owned_groups")
    members = relationship("User", secondary=user_groups, back_populates="groups")
    lawyer_members = relationship(
        "Lawyer", secondary=lawyer_groups, back_populates="groups"
    )
    messages = relationship(
        "GroupMessage", back_populates="group", cascade="all, delete-orphan"
    )
    consultations = relationship(
        "Consultation", back_populates="group", cascade="all, delete-orphan"
    )


class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    lawyer_author_id = Column(
        Integer, ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    group = relationship("Group", back_populates="messages")
    author = relationship("User", back_populates="group_messages")
    lawyer_author = relationship("Lawyer", back_populates="group_messages")
