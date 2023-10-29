import json
from app.tests.conftest import add_user, get_user_token_headers, test_data


def test_user_create_success(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.post(
        "/api/users",
        data={"username": "new_user", "password": test_data},
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "new_user"


def test_user_create_failure(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.post(
        "/api/users",
        data={"username": test_data, "password": test_data},
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Пользователь с таким именем уже существует"


def test_user_get_success(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.get(
        "/api/users",
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_user_without_permission(client, db_session):
    response = client.get(
        "/api/users",
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_user_delete_success(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    add_user(db_session, username="new_user", password=test_data)
    response = client.delete(
        "/api/users/2",
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_update_user_success(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    add_user(db_session, username="new_user", password=test_data)
    response = client.put(
        "/api/users/",
        headers=get_user_token_headers(username=test_data),
        content=json.dumps({"user_id": 2, "username": "new_username", "password": test_data}),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "new_username"


def test_update_user_same_name_failure(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    add_user(db_session, username="new_user", password=test_data)
    response = client.put(
        "/api/users/",
        headers=get_user_token_headers(username=test_data),
        content=json.dumps({"user_id": 1, "username": "new_user", "password": test_data}),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == 'Пользователь с именем new_user уже существует'


def test_get_user_by_username_success(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.get(
        "/api/users/?username=test",
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 200
    assert response.json()[0]["username"] == test_data


def test_get_user_by_id(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.get(
        "/api/users/?user_id=1",
        headers=get_user_token_headers(username=test_data),
    )
    assert response.status_code == 200
    assert response.json()[0]["username"] == test_data
