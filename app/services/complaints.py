from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Protocol

import ollama
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.complaint import ComplaintCreate, ComplaintTicket, TicketStatus, TriageResult

SYSTEM_PROMPT = """You are an enterprise banking complaint triage system.
Analyze the customer complaint and return ONLY a JSON object that matches the schema.
Rules:
- Pick exactly one category: "ATM / Card Issue", "Account Balance", "Fraud", or "General".
- ATM cash not dispensed but the account was still debited is "ATM / Card Issue" with urgency High or Critical.
- Suspected unauthorized activity, stolen cards, or phishing is "Fraud" with urgency High or Critical.
- Do not invent account numbers, amounts, phone numbers, emails, or other facts that are not in the complaint.
- suggested_reply must be professional, empathetic, and ready to send. Promise a follow-up instead of fake contact details.
"""


class ComplaintNotFoundError(Exception):
    def __init__(self, complaint_id: int):
        self.complaint_id = complaint_id
        super().__init__(f"Complaint {complaint_id} not found")


class OllamaUnavailableError(Exception):
    def __init__(self, message: str = "Ollama is unavailable"):
        super().__init__(message)


class TriageFailedError(Exception):
    def __init__(self, message: str = "Could not triage the complaint"):
        super().__init__(message)


class ChatClient(Protocol):
    def chat(self, **kwargs: object) -> object: ...


def _message_content(response: object) -> str:
    if isinstance(response, dict):
        return str(response["message"]["content"])
    message = getattr(response, "message")
    return str(message.content)


def _parse_triage(content: str) -> TriageResult:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TriageFailedError("Model did not return valid JSON") from exc
    try:
        return TriageResult.model_validate(payload)
    except ValidationError as exc:
        raise TriageFailedError("Model JSON did not match the triage schema") from exc


class ComplaintService:
    def __init__(self, client: ChatClient | None = None) -> None:
        self._client = client or ollama.Client(
            host=settings.ollama_host,
            timeout=settings.ollama_timeout,
        )
        self._tickets: dict[int, ComplaintTicket] = {}
        self._next_id = 1

    def list_complaints(
        self,
        urgency: str | None = None,
        status: TicketStatus | None = None,
    ) -> list[ComplaintTicket]:
        tickets = list(self._tickets.values())
        if urgency is not None:
            tickets = [ticket for ticket in tickets if ticket.urgency == urgency]
        if status is not None:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        return tickets

    def get_complaint(self, complaint_id: int) -> ComplaintTicket:
        ticket = self._tickets.get(complaint_id)
        if ticket is None:
            raise ComplaintNotFoundError(complaint_id)
        return ticket

    def create_complaint(self, payload: ComplaintCreate) -> ComplaintTicket:
        triage = self._triage(payload.complaint)
        ticket = ComplaintTicket(
            id=self._next_id,
            complaint=payload.complaint,
            customer_name=payload.customer_name,
            channel=payload.channel,
            status="open",
            model=settings.ollama_model,
            created_at=datetime.now(UTC),
            **triage.model_dump(),
        )
        self._tickets[ticket.id] = ticket
        self._next_id += 1
        return ticket

    def update_status(self, complaint_id: int, status: TicketStatus) -> ComplaintTicket:
        ticket = self.get_complaint(complaint_id)
        updated = ticket.model_copy(update={"status": status})
        self._tickets[complaint_id] = updated
        return updated

    def _triage(self, complaint: str) -> TriageResult:
        try:
            response = self._client.chat(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": complaint},
                ],
                format=TriageResult.model_json_schema(),
                options={"temperature": 0},
            )
        except Exception as exc:
            raise OllamaUnavailableError("Could not reach Ollama") from exc
        return _parse_triage(_message_content(response))


complaint_service = ComplaintService()
