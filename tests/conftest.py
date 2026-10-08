import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.complaints import ComplaintService, complaint_service
from app.services.items import ItemService, item_service


@pytest.fixture
def client() -> TestClient:
    item_service.__dict__.update(ItemService().__dict__)
    complaint_service.__dict__.update(ComplaintService().__dict__)
    return TestClient(app)
