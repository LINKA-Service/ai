import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CaseType(str, enum.Enum):
    DELIVERY = "delivery"
    INSURANCE = "insurance"
    DOOR_TO_DOOR = "door_to_door"
    APPOINTMENT = "appointment"
    RENTAL = "rental"
    ROMANCE = "romance"
    SMISHING = "smishing"
    FALSE_ADVERTISING = "false_advertising"
    SECONDHAND_FRAUD = "secondhand_fraud"
    INVESTMENT_SCAM = "investment_scam"
    ACCOUNT_TAKEOVER = "account_takeover"
    OTHER = "other"


class LowerCaseEnum(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, str):
            return value.lower()
        return str(value).lower()

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.enum_class(value)
        return value


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    case_type = Column(LowerCaseEnum(CaseType, length=50), nullable=False)
    case_type_other = Column(String(100), nullable=True)
    title = Column(String(200), nullable=False)

    statement = Column(Text, nullable=False)

    status = Column(
        LowerCaseEnum(CaseStatus, length=20), default=CaseStatus.PENDING, nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="cases")
    scammer_infos = relationship(
        "ScammerInfo", back_populates="case", cascade="all, delete-orphan"
    )


class ScammerInfoType(str, enum.Enum):
    NAME = "name"
    NICKNAME = "nickname"
    PHONE = "phone"
    ACCOUNT = "account"
    SNS_ID = "sns_id"


class ScammerInfo(Base):
    __tablename__ = "scammer_infos"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    info_type = Column(LowerCaseEnum(ScammerInfoType, length=20), nullable=False)
    value = Column(String(200), nullable=False)

    case = relationship("Case", back_populates="scammer_infos")
