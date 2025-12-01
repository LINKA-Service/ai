import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.database import Base


class CaseStatus(str, enum.Enum):
    PENDING = "pending"  # 검토 중
    APPROVED = "approved"  # 승인됨
    REJECTED = "rejected"  # 거부됨


class CaseType(str, enum.Enum):
    DELIVERY = "delivery"  # 직거래 사기
    INSURANCE = "insurance"  # 보험/서류 사기
    DOOR_TO_DOOR = "door_to_door"  # 방문판매 사기
    APPOINTMENT = "appointment"  # 사칭/위조 사기
    RENTAL = "rental"  # 전세/월세 사기
    ROMANCE = "romance"  # 로맨스 스캠
    SMISHING = "smishing"  # 스미싱 사기
    FALSE_ADVERTISING = "false_advertising"  # 허위 광고 사기
    SECONDHAND_FRAUD = "secondhand_fraud"  # 중고거래 사기
    INVESTMENT_SCAM = "investment_scam"  # 투자 유인 사기
    ACCOUNT_TAKEOVER = "account_takeover"  # 계정 도용 사기
    OTHER = "other"  # 기타


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    case_type = Column(SQLEnum(CaseType), nullable=False)  # 피해 종류
    case_type_other = Column(String(100), nullable=True)  # 기타 피해 종류
    title = Column(String(200), nullable=False)  # 진술 기반으로 AI가 생성한 사건명

    statement = Column(Text, nullable=False)  # 진술

    status = Column(
        SQLEnum(CaseStatus), default=CaseStatus.PENDING, nullable=False
    )  # AI가 검토 후 수상하면 운영자 검토로 감

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
    NAME = "name"  # 이름
    NICKNAME = "nickname"  # 닉네임
    PHONE = "phone"  # 전화번호
    ACCOUNT = "account"  # 계좌번호
    SNS_ID = "sns_id"  # SNS ID


class ScammerInfo(Base):
    __tablename__ = "scammer_infos"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    info_type = Column(SQLEnum(ScammerInfoType), nullable=False)
    value = Column(String(200), nullable=False)

    case = relationship("Case", back_populates="scammer_infos")
