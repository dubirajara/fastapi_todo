from time import sleep

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


def test_update_user(db):
    user = db.scalar(select(User).where(User.id == 1))
    previous_update_at = user.updated_at

    assert user.username == 'JohnDoe'
    assert user.email == 'john@doe.com'
    assert user.password == 'password123'
    assert user.updated_at

    sleep(1)

    user.password = 'password42'
    db.add(user)
    db.commit()

    assert user.id == 1
    assert user.password == 'password42'
    assert user.username == 'JohnDoe'
    assert user.email == 'john@doe.com'
    assert user.updated_at > previous_update_at
