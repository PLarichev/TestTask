from app.tests.conftest import add_user, test_data


def test_login_success(client, db_session):
    add_user(db_session)
    response = client.post(
        "/api/login",
        data={"username": test_data, "password": test_data},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_failure(client, db_session):
    add_user(db_session)
    response = client.post(
        "/api/login",
        data={"username": test_data, "password": "wrong password"},
    )
    assert response.status_code == 401


def test_signup_success(client):
    response = client.post(
        "/api/signup",
        data={"username": test_data, "password": test_data},
    )
    assert response.status_code == 200
    assert response.json()["user_id"]


def test_signup_failure(client, db_session):
    add_user(db_session)
    response = client.post(
        "api/signup",
        data={"username": test_data, "password": test_data}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Пользователь с таким именем уже существует"
