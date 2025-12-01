from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConsultationMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class ConsultationMessageResponse(BaseModel):
    id: int
    content: str
    consultation_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConsultationCreate(BaseModel):
    case_id: int
    name: str = Field(..., max_length=200)
    group_id: Optional[int] = None


class ConsultationResponse(BaseModel):
    id: int
    case_id: int
    name: str
    author_id: int
    group_id: Optional[int]
    created_at: datetime
    messages: List[ConsultationMessageResponse] = []

    class Config:
        from_attributes = True
