from fastapi.testclient import TestClient


def test_create_and_get_item(client: TestClient) -> None:
    created = client.post(
        "/api/items",
        json={"name": "Notebook", "description": "A5 lined", "price": 12.5},
    )
    assert created.status_code == 201
    item = created.json()
    assert item["id"] == 1
    assert item["name"] == "Notebook"

    fetched = client.get(f"/api/items/{item['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["price"] == 12.5


def test_list_update_and_delete_item(client: TestClient) -> None:
    client.post("/api/items", json={"name": "Pen", "price": 2.0})
    listed = client.get("/api/items")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch("/api/items/1", json={"price": 2.5})
    assert updated.status_code == 200
    assert updated.json()["price"] == 2.5

    deleted = client.delete("/api/items/1")
    assert deleted.status_code == 204
    missing = client.get("/api/items/1")
    assert missing.status_code == 404
