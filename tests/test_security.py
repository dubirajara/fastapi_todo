from jwt import decode

from fastapi_todo.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)
    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert decoded['sub'] == data['sub']
    assert decoded['exp']
