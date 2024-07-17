from http import HTTPStatus
from unittest.mock import ANY

import pytest

from fastapi_todo.models import TodoState
from tests.conftest import TodoFactory

# Success test cases


def test_create_todo(client, access_token):
    payload = {
        'title': 'test todo',
        'description': 'test todo description',
        'state': 'draft',
    }
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {access_token}'},
        json=payload,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'test todo',
        'description': 'test todo description',
        'state': 'draft',
        'created_at': ANY,
        'updated_at': ANY,
    }


def test_get_todos(client, access_token, session, user):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()
    expected_todos = 5
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_get_todos_pagination(client, access_token, session, user):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()
    expected_todos = 2
    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.parametrize(
    'fields',  # noqa
    [
        ({'title': 'Test todo 1'}),
        ({'description': 'test description'}),
        ({'state': TodoState.DOING}),
    ],
)
def test_get_todos_filter_query(  # noqa
    fields, client, access_token, session, user
):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, **fields)
    )
    session.commit()
    expected_todos = 5
    field, value = *fields.keys(), *fields.values()
    response = client.get(
        f'/todos/?{field}={value}',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, access_token
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.DONE,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.TODO,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(session, client, user, access_token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_delete_todo_error(client, access_token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo_error(client, access_token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo(session, client, user, access_token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'
