from http import HTTPStatus

from fastapi_todo.schemas import UserPublic

# Success test cases


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
    assert response.json() == {'users': []}
    assert response.status_code == HTTPStatus.OK


def test_get_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}
    assert response.status_code == HTTPStatus.OK


def test_update_user(client, user, access_token):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put(
        f'/users/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.json() == {
        'email': 'testuser@mail.com',
        'id': 1,
        'username': 'testuser',
    }
    assert response.status_code == HTTPStatus.OK


def test_get_user(client, user):
    response = client.get('/users/1')
    assert response.json() == {
        'email': 'Testjohn@doe.com',
        'id': 1,
        'username': 'TestJohnDoe',
    }

    assert response.status_code == HTTPStatus.OK


def test_delete_user(client, user, access_token):
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.json() == {'message': 'User deleted'}
    assert response.status_code == HTTPStatus.OK


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.username, 'password': user.plain_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


# Failure test cases


def test_create_user_username_exists(client, user):
    payload = {
        'username': 'TestJohnDoe',
        'email': 'john@doe.com',
        'password': 'password123',
    }
    response = client.post('/users/', json=payload)
    assert response.json() == {'detail': 'Username already exists'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_user_email_exists(client, user):
    payload = {
        'username': 'JohnDoe',
        'email': 'Testjohn@doe.com',
        'password': 'password123',
    }
    response = client.post('/users/', json=payload)
    assert response.json() == {'detail': 'Email already exists'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_update_user_not_own(client, user, access_token):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put(
        '/users/2',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.json() == {'detail': 'You can only update your own user'}
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_user_invalid_token(client):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put(
        '/users/1',
        json=payload,
        headers={'Authorization': 'Bearer testtoken'},
    )
    assert response.json() == {'detail': 'Invalid credentials'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_user_not_authenticated(client, user):
    payload = {
        'username': 'testuser',
        'email': 'testuser@mail.com',
        'password': '42',
    }
    response = client.put(
        '/users/2',
        json=payload,
    )
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_user_not_found(client, user):
    response = client.get('/users/2')
    assert response.json() == {'detail': 'User not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_not_own(client, user, access_token):
    response = client.delete(
        '/users/2', headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.json() == {'detail': 'You can only delete your own user'}
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user_not_authenticated(client, user):
    response = client.delete('/users/2')
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_token_invalid_credentials(client, user):
    response = client.post(
        '/token',
        data={'username': user.username, 'password': '42'},
    )

    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == HTTPStatus.BAD_REQUEST
