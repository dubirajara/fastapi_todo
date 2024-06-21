import pytest
from fastapi.testclient import TestClient

from fastapi_todo.app import app


@pytest.fixture()
def client():
    return TestClient(app)
