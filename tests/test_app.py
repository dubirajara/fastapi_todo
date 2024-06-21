from http import HTTPStatus

# Success test cases


def test_read_root_status_code_and_message_ok(client):
    response = client.get('/')
    assert response.json() == {'message': 'Hello World'}
    assert response.status_code == HTTPStatus.OK


def test_read_hello_status_code_and_message_ok(client):
    response = client.get('/hello')
    assert (
        response.text
        == """
    <html>
        <head>
            <title>Hello World</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    """
    )
    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'


def test_create_user(client):
    payload = {
        'username': 'JohnDoe',
        'email': 'john@doe.com',
        'password': 'password123',
    }
    response = client.post('/users/', json=payload)
    assert response.json() == {
        'email': 'john@doe.com',
        'id': 1,
        'username': 'JohnDoe',
    }
    assert response.status_code == HTTPStatus.CREATED


def test_get_users(client):
    response = client.get('/users/')
    assert response.json() == {
        'users': [
            {
                'email': 'john@doe.com',
                'id': 1,
                'username': 'JohnDoe',
            }
        ]
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user(client):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put('/users/1', json=payload)
    assert response.json() == {
        'email': 'testuser@mail.com',
        'id': 1,
        'username': 'testuser',
    }
    assert response.status_code == HTTPStatus.OK


def test_get_user(client):
    response = client.get('/users/1')
    assert response.json() == {
        'email': 'testuser@mail.com',
        'id': 1,
        'username': 'testuser',
    }

    assert response.status_code == HTTPStatus.OK


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.json() == {'message': 'User deleted'}
    assert response.status_code == HTTPStatus.OK


# Failure test cases
def test_update_user_not_found(client):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put('/users/2', json=payload)
    assert response.json() == {'detail': 'User not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_not_found(client):
    response = client.get('/users/2')
    assert response.json() == {'detail': 'User not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_not_found(client):
    response = client.delete('/users/2')
    assert response.json() == {'detail': 'User not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND
