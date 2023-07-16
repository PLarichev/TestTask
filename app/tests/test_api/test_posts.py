import json
from app.tests.conftest import add_user, add_post, get_user_token_headers, test_data


def test_get_posts_without_records(client, db_session):
    add_user(db_session, username=test_data, password=test_data)
    response = client.get(
        "/api/posts",
        headers=get_user_token_headers(username=test_data)
    )
    assert response.status_code == 404
    assert response.json()["detail"] == 'Не существует ни одной публикации'


def test_create_and_get_posts_with_records(client, db_session):
    add_user(db_session)
    client.post(
        "/api/posts",
        headers=get_user_token_headers(username=test_data),
        content=json.dumps({"post_content": test_data})
    )
    response = client.get(
        "/api/posts",
        headers=get_user_token_headers(username=test_data)
    )
    assert response.status_code == 200
    assert response.json()["posts"]


def test_edit_post_success(client, db_session):
    user = add_user(db_session)
    add_post(db_session, user_fk=user.user_id)
    response = client.put(
        "/api/posts",
        headers=get_user_token_headers(username=test_data),
        content=json.dumps({"post_id": 1, "post_content": "something_new"})
    )
    assert response.status_code == 200
    assert response.json()["post_content"] == "something_new"


def test_edit_not_owner_post(client, db_session):
    user = add_user(db_session)
    user2 = add_user(db_session, username="test2", password="test2")
    add_post(db_session, user_fk=user2.user_id)
    response = client.put(
        "/api/posts",
        headers=get_user_token_headers(username=user.username),
        content=json.dumps({"post_id": 1, "post_content": "throw_forbidden"})
    )
    assert response.status_code == 403


def test_delete_post_success(client, db_session):
    user = add_user(db_session)
    post = add_post(db_session, user_fk=user.user_id)
    add_post(db_session, user_fk=user.user_id)
    response = client.delete(
        f"/api/posts/{post.post_id}",
        headers=get_user_token_headers(test_data),
    )
    assert response.status_code == 200
    assert len(response.json()["posts"]) == 1


def test_delete_not_owner_post(client, db_session):
    user = add_user(db_session)
    user2 = add_user(db_session, username="test2")
    post = add_post(db_session, user_fk=user2.user_id)
    response = client.delete(
        f"/api/posts/{post.post_id}",
        headers=get_user_token_headers(username=user.username)
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Вы не можете удалить не свой пост / Не хватает прав на редактирование"
