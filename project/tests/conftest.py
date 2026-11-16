import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SKYROUTE_DB", str(tmp_path / "test.db"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(app) as c:
        yield c
