from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.case import CaseType, SQLEnum

lawyer_groups = Table(
    "lawyer_groups",
    Base.metadata,
    Column("lawyer_id", Integer, ForeignKey("lawyers.id", ondelete="CASCADE")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
)


class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(String, unique=True, index=True, nullable=False)
    lawyer_id_changed_at = Column(DateTime(timezone=True), nullable=True)
    hashed_password = Column(String, nullable=False)
    lawyer_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    specializations = Column(SQLEnum(CaseType), nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    groups = relationship(
        "Group", secondary=lawyer_groups, back_populates="lawyer_members"
    )
    group_messages = relationship(
        "GroupMessage", back_populates="lawyer_author", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "LawyerReview", back_populates="lawyer", cascade="all, delete-orphan"
    )


class LawyerReview(Base):
    __tablename__ = "lawyer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(
        Integer, ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_type = Column(SQLEnum(CaseType), nullable=False)
    review = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    author = relationship("User", back_populates="reviews")
    lawyer = relationship("Lawyer", back_populates="reviews")
