from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.case import CaseStatus, CaseType, ScammerInfoType


class ScammerInfoCreate(BaseModel):
    info_type: ScammerInfoType
    value: str = Field(..., max_length=200)


class ScammerInfoResponse(BaseModel):
    id: int
    case_id: int
    info_type: ScammerInfoType
    value: str

    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    case_type: CaseType
    case_type_other: Optional[str]
    statement: str
    scammer_infos: List[ScammerInfoCreate] = []


class CaseResponse(BaseModel):
    id: int
    user_id: int
    case_type: CaseType
    case_type_other: Optional[str]
    title: str
    statement: str
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    scammer_infos: List[ScammerInfoResponse]

    class Config:
        from_attributes = True
