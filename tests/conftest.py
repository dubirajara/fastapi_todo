import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_todo.app import app
from fastapi_todo.models import table_registry


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(scope='session')
def db():
    engine = create_engine('sqlite:///:memory:')

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
