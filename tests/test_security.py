from http import HTTPStatus

from jwt import decode

from fastapi_todo.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded['sub'] == data['sub']
    assert decoded['exp']


def test_invalid_token_user_not_exists(client, user, access_token):
    client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.json() == {'detail': 'Invalid credentials'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED
