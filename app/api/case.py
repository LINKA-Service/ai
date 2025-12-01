from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_case_service, get_current_user, get_db
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse, SimilarCaseResponse
from app.services.case_service import CaseService

router = APIRouter()


@router.get("/", response_model=List[CaseResponse])
async def list_my_cases(
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return case_service.get_user_cases(current_user.id)


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(
    case_data: CaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    print(case_data)
    case = case_service.create_case(case_data, current_user.id)
    return case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case_detail(
    case_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return case_service.get_user_case(case_id, current_user.id)


@router.delete("/{case_id}")
async def delete_case_by_id(
    case_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    case_service.delete_case(case_id, current_user.id)
    return {"message": "Case deleted successfully"}


@router.get("/{case_id}/similar", response_model=List[SimilarCaseResponse])
def get_similar_cases(
    case_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CaseService(db)
    return service.get_similar_cases(case_id, current_user.id, limit)
