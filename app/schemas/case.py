from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

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


from pydantic import model_validator


class CaseCreate(BaseModel):
    case_type: CaseType
    case_type_other: Optional[str] = None
    statement: str
    scammer_infos: List[ScammerInfoCreate] = []

    @model_validator(mode="after")
    def validate_case_type_other(self):
        if self.case_type == CaseType.OTHER and not self.case_type_other:
            raise ValueError("case_type_other is required when case_type is OTHER")
        if self.case_type != CaseType.OTHER and self.case_type_other:
            raise ValueError(
                "case_type_other should only be provided when case_type is OTHER"
            )
        return self


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


class SimilarCaseResponse(BaseModel):
    case_id: int
    title: str
    case_type: str
    statement: str
    scammer_infos: List[dict]
    similarity_score: float
    created_at: Optional[str]
