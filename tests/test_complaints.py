from fastapi.testclient import TestClient

from app.services.complaints import complaint_service


SAMPLE_COMPLAINT = (
    "I tried to withdraw $200 from the ATM, but the machine malfunctioned "
    "and didn't dispense the cash. However, my account was still debited!"
)

TRIAGE = {
    "category": "ATM / Card Issue",
    "urgency": "High",
    "sentiment": "Frustrated",
    "root_cause_summary": "ATM failed to dispense cash but still debited the account.",
    "suggested_reply": (
        "I'm sorry this happened. We will investigate the ATM withdrawal, "
        "protect your account, and follow up with the debit as a priority."
    ),
}


class FakeChatClient:
    def __init__(self, content: str | None = None, error: Exception | None = None) -> None:
        self.content = content
        self.error = error
        self.calls: list[dict] = []

    def chat(self, **kwargs: object) -> dict:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return {"message": {"content": self.content}}


def test_create_and_get_complaint(client: TestClient) -> None:
    import json

    complaint_service._client = FakeChatClient(content=json.dumps(TRIAGE))

    created = client.post(
        "/api/complaints",
        json={"complaint": SAMPLE_COMPLAINT, "channel": "atm"},
    )
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["id"] == 1
    assert ticket["category"] == "ATM / Card Issue"
    assert ticket["urgency"] == "High"
    assert ticket["status"] == "open"
    assert ticket["channel"] == "atm"
    assert "suggested_reply" in ticket

    fetched = client.get("/api/complaints/1")
    assert fetched.status_code == 200
    assert fetched.json()["complaint"] == SAMPLE_COMPLAINT


def test_list_filter_and_update_status(client: TestClient) -> None:
    import json

    complaint_service._client = FakeChatClient(content=json.dumps(TRIAGE))
    client.post("/api/complaints", json={"complaint": SAMPLE_COMPLAINT})

    listed = client.get("/api/complaints")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    high = client.get("/api/complaints", params={"urgency": "High"})
    assert len(high.json()) == 1

    low = client.get("/api/complaints", params={"urgency": "Low"})
    assert low.json() == []

    updated = client.patch("/api/complaints/1", json={"status": "resolved"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"


def test_rejects_short_complaint(client: TestClient) -> None:
    response = client.post("/api/complaints", json={"complaint": "too short"})
    assert response.status_code == 422


def test_ollama_unavailable(client: TestClient) -> None:
    complaint_service._client = FakeChatClient(error=ConnectionError("down"))
    response = client.post("/api/complaints", json={"complaint": SAMPLE_COMPLAINT})
    assert response.status_code == 503


def test_invalid_model_json(client: TestClient) -> None:
    complaint_service._client = FakeChatClient(content="not json")
    response = client.post("/api/complaints", json={"complaint": SAMPLE_COMPLAINT})
    assert response.status_code == 502


def test_missing_complaint(client: TestClient) -> None:
    response = client.get("/api/complaints/99")
    assert response.status_code == 404
