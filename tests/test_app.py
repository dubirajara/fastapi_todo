from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_todo.app import app

client = TestClient(app)


def test_read_root_status_code_and_message_ok():
    response = client.get('/')
    assert response.json() == {'message': 'Hello World'}
    assert response.status_code == HTTPStatus.OK


def test_read_hello_status_code_and_message_ok():
    response = client.get('/hello')
    assert response.text == """
    <html>
        <head>
            <title>Hello World</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    """
    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
