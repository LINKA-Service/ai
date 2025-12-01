from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_consultation_service, get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.user import User
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationMessageCreate,
    ConsultationMessageResponse,
    ConsultationResponse,
)
from app.services.consultation_service import ConsultationService

router = APIRouter()


@router.get("/", response_model=List[ConsultationResponse])
async def list_my_consultations(
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    return consultation_service.get_user_consultations(current_user.id)


@router.post("/", response_model=ConsultationResponse, status_code=201)
async def create_consultation(
    consultation_data: ConsultationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    consultation = consultation_service.create_consultation(
        consultation_data, current_user.id
    )
    return consultation


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation_detail(
    consultation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    consultation = consultation_service.get_consultation(consultation_id)
    if not consultation:
        raise NotFoundException("Consultation not found")

    if not consultation_service.can_access_consultation(
        consultation_id, current_user.id
    ):
        raise ForbiddenException("Access denied")

    return consultation


@router.delete("/{consultation_id}")
async def delete_consultation(
    consultation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    consultation_service.delete_consultation(consultation_id, current_user.id)
    return {"message": "Consultation deleted successfully"}


@router.get(
    "/{consultation_id}/messages", response_model=List[ConsultationMessageResponse]
)
async def get_consultation_messages(
    consultation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    consultation = consultation_service.get_consultation(consultation_id)
    if not consultation:
        raise NotFoundException("Consultation not found")

    if not consultation_service.can_access_consultation(
        consultation_id, current_user.id
    ):
        raise ForbiddenException("Access denied")

    return consultation_service.get_consultation_messages(consultation_id, skip, limit)


@router.post(
    "/{consultation_id}/messages",
    response_model=ConsultationMessageResponse,
    status_code=201,
)
async def create_consultation_message(
    consultation_id: int,
    message_data: ConsultationMessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    message = consultation_service.create_message(
        consultation_id, message_data, current_user.id
    )
    return message


@router.delete("/{consultation_id}/messages/{message_id}")
async def delete_consultation_message(
    consultation_id: int,
    message_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    consultation_service.delete_message(message_id, current_user.id)
    return {"message": "Message deleted successfully"}


@router.post(
    "/{consultation_id}/messages/ai",
    response_model=ConsultationMessageResponse,
    status_code=201,
)
async def create_ai_consultation_message(
    consultation_id: int,
    message_data: ConsultationMessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    consultation_service: Annotated[
        ConsultationService, Depends(get_consultation_service)
    ],
):
    message = consultation_service.create_ai_message(
        consultation_id, message_data.content, current_user.id
    )
    return message
