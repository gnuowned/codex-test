import importlib
import os

import pytest
from starlette.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Use isolated DB per test
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    # Reload modules to pick up new DB path
    from app import database

    importlib.reload(database)

    from app import main

    importlib.reload(main)

    return TestClient(main.app)


def test_create_and_list(client: TestClient):
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    resp = client.post("/customers", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]

    list_resp = client.get("/customers")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["email"] == payload["email"]


def test_duplicate_email_returns_400(client: TestClient):
    payload = {"name": "Ada", "email": "ada@example.com"}
    assert client.post("/customers", json=payload).status_code == 201
    resp_dup = client.post("/customers", json=payload)
    assert resp_dup.status_code == 400
    assert resp_dup.json()["detail"] == "email already exists"


def test_update_customer(client: TestClient):
    payload = {"name": "Ada", "email": "ada@example.com"}
    created = client.post("/customers", json=payload).json()
    update_resp = client.put(
        f"/customers/{created['id']}", json={"status": "inactive", "notes": "paused"}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["status"] == "inactive"
    assert updated["notes"] == "paused"


def test_delete_customer(client: TestClient):
    created = client.post("/customers", json={"name": "Ada", "email": "ada@example.com"}).json()
    del_resp = client.delete(f"/customers/{created['id']}")
    assert del_resp.status_code == 204
    missing = client.get(f"/customers/{created['id']}")
    assert missing.status_code == 404
