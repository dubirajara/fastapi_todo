from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_todo.app import app

client = TestClient(app)


def test_read_root_status_code_and_message_ok():
    response = client.get('/')
    assert response.json() == {'message': 'Hello World'}
    assert response.status_code == HTTPStatus.OK
