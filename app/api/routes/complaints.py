from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintStatusUpdate,
    ComplaintTicket,
    TicketStatus,
    Urgency,
)
from app.services.complaints import (
    ComplaintNotFoundError,
    OllamaUnavailableError,
    TriageFailedError,
    complaint_service,
)

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.get("", response_model=list[ComplaintTicket])
def list_complaints(
    urgency: Annotated[Urgency | None, Query()] = None,
    ticket_status: Annotated[TicketStatus | None, Query(alias="status")] = None,
) -> list[ComplaintTicket]:
    return complaint_service.list_complaints(urgency=urgency, status=ticket_status)


@router.get("/{complaint_id}", response_model=ComplaintTicket)
def get_complaint(complaint_id: int) -> ComplaintTicket:
    try:
        return complaint_service.get_complaint(complaint_id)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=ComplaintTicket, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate) -> ComplaintTicket:
    try:
        return complaint_service.create_complaint(payload)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except TriageFailedError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.patch("/{complaint_id}", response_model=ComplaintTicket)
def update_complaint_status(
    complaint_id: int,
    payload: ComplaintStatusUpdate,
) -> ComplaintTicket:
    try:
        return complaint_service.update_status(complaint_id, payload.status)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
