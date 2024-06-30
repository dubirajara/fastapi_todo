from sqlalchemy import select

from fastapi_todo.models import User


def test_create_user(db):
    user = User(
        username='JohnDoe', password='password123', email='john@doe.com'
    )
    db.add(user)
    db.commit()
    result = db.scalar(select(User).where(User.username == 'JohnDoe'))

    assert result.username == 'JohnDoe'
    assert result.email == 'john@doe.com'
    assert result.password == 'password123'
