from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["ATM / Card Issue", "Account Balance", "Fraud", "General"]
Urgency = Literal["Low", "Medium", "High", "Critical"]
Sentiment = Literal["Frustrated", "Angry", "Neutral"]
TicketStatus = Literal["open", "in_review", "resolved"]


class ComplaintCreate(BaseModel):
    complaint: str = Field(min_length=10, max_length=4000)
    customer_name: str | None = Field(default=None, max_length=120)
    channel: str | None = Field(
        default=None,
        max_length=40,
        description="Where the complaint arrived, e.g. atm, email, phone, chat",
    )


class TriageResult(BaseModel):
    category: Category
    urgency: Urgency
    sentiment: Sentiment
    root_cause_summary: str = Field(min_length=1, max_length=500)
    suggested_reply: str = Field(min_length=1, max_length=2000)


class ComplaintTicket(TriageResult):
    id: int
    complaint: str
    customer_name: str | None
    channel: str | None
    status: TicketStatus = "open"
    model: str
    created_at: datetime


class ComplaintStatusUpdate(BaseModel):
    status: TicketStatus
