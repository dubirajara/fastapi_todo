import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fastapi_todo.app import app
from fastapi_todo.database import get_session
from fastapi_todo.models import Todo, TodoState, User, table_registry
from fastapi_todo.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def persist_user(session, password):
    user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    user.plain_password = password  # Monkey Patch
    return user


@pytest.fixture()
def client(session):
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = lambda: session
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture()
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()

    table_registry.metadata.drop_all(engine)


@pytest.fixture()
def user(session):
    return persist_user(session, 'Testpassword123')


@pytest.fixture()
def other_user(session):
    return persist_user(session, 'Testpassword123')


@pytest.fixture()
def access_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.plain_password},
    )
    return response.json()['access_token']
