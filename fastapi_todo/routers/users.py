from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_todo.database import get_session
from fastapi_todo.models import User
from fastapi_todo.schemas import (
    Message,
    UserListPublic,
    UserPublic,
    UserSchema,
)
from fastapi_todo.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[Session, Depends(get_session)]

T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )
        elif db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserListPublic)
def get_users(session: T_Session, limit: int = 10, offset: int = 0):
    db_user = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': db_user}


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def get_user(user_id: int, session: T_Session):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    curret_user: T_CurrentUser,
):
    if curret_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You can only update your own user',
        )

    curret_user.username = user.username
    curret_user.password = get_password_hash(user.password)
    curret_user.email = user.email

    session.commit()
    session.refresh(curret_user)

    return curret_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    curret_user: T_CurrentUser,
):
    if curret_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You can only delete your own user',
        )

    session.delete(curret_user)
    session.commit()

    return {'message': 'User deleted'}
