from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.plain_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'Bearer'


def test_get_token_invalid_credentials(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': '42'},
    )

    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == HTTPStatus.BAD_REQUEST
