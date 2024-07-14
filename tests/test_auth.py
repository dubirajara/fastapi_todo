from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.plain_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


def test_get_token_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': '42'},
    )

    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_token_invalid_user(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'Wrong_username', 'password': user.plain_password},
    )

    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_token_expired_token(client, user):
    with freeze_time('2023-01-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.plain_password},
        )

    token = response.json()['access_token']
    assert response.status_code == HTTPStatus.OK

    with freeze_time('2023-01-01 12:31:00'):
        response = client.delete(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.json() == {'detail': 'Invalid credentials'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token(client, access_token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


def test_token_expire_not_refresh(client, user):
    with freeze_time('2023-01-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.plain_password},
        )

    token = response.json()['access_token']
    assert response.status_code == HTTPStatus.OK

    with freeze_time('2023-01-01 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.json() == {'detail': 'Invalid credentials'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED
