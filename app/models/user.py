from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    username_changed_at = Column(DateTime(timezone=True), nullable=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    groups = relationship("Group", secondary=user_groups, back_populates="members")
    owned_groups = relationship(
        "Group", back_populates="owner", cascade="all, delete-orphan"
    )
    group_messages = relationship(
        "GroupMessage", back_populates="author", cascade="all, delete-orphan"
    )
    cases = relationship("Case", back_populates="user", cascade="all, delete-orphan")
    consultations = relationship(
        "Consultation", back_populates="author", cascade="all, delete-orphan"
    )
    consultation_messages = relationship(
        "ConsultationMessage", back_populates="author", cascade="all, delete-orphan"
    )
    reviews = relationship("LawyerReview", back_populates="author", cascade="all, delete-orphan")
