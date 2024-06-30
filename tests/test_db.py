from time import sleep

from sqlalchemy import select

from fastapi_todo.models import User


def test_create_user(session):
    user = User(
        username='JohnDoe', password='password123', email='john@doe.com'
    )
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.username == 'JohnDoe'))

    assert result.username == 'JohnDoe'
    assert result.email == 'john@doe.com'
    assert result.password == 'password123'


def test_update_user(session, user):
    user_db = session.scalar(select(User).where(User.id == user.id))
    previous_update_at = user_db.updated_at

    assert user_db.username == 'TestJohnDoe'
    assert user_db.email == 'Testjohn@doe.com'
    assert user_db.password == 'Testpassword123'
    assert user_db.updated_at

    sleep(1)

    user.password = 'password42'
    session.add(user)
    session.commit()

    assert user.id == 1
    assert user.password == 'password42'
    assert user.updated_at > previous_update_at
