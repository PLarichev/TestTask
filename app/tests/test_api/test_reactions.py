from app.tests.conftest import add_user, add_post, add_reaction, get_user_token_headers, test_data


def test_post_and_get_reactions_success(client, db_session):
    user = add_user(db_session)
    user2 = add_user(db_session, username="test2")
    post = add_post(db_session, user_fk=user.user_id)
    add_reaction(db_session, post_fk=post.post_id, user_fk=user.user_id)
    response = client.post(
        "/api/reaction",
        headers=get_user_token_headers(username=user2.username),
        json={"post_id": post.post_id, "user_fk": user2.user_id, "reaction": "dislike"},
    )
    assert response.status_code == 200
    assert response.json()["reaction_id"] == 2

    response = client.get("/api/reaction/1",
                          headers=get_user_token_headers(username=test_data))
    assert response.json() == "Количество лайков для поста: 1, количество дизлайков: 1"
    assert response.status_code == 200


def test_post_second_reaction_error(client, db_session):
    user = add_user(db_session)
    post = add_post(db_session, user_fk=user.user_id)
    add_reaction(db_session, user_fk=user.user_id, post_fk=post.post_id)
    response = client.post(
        "/api/reaction",
        headers=get_user_token_headers(username=user.username),
        json={"post_id": post.post_id, "user_fk": user.user_id, "reaction": "like"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Нельзя поставить больше одной реакции на публикацию"


def test_put_reaction_success(client, db_session):
    user = add_user(db_session)
    post = add_post(db_session, user_fk=user.user_id)
    reaction = add_reaction(db_session, user_fk=user.user_id, post_fk=post.post_id)
    response = client.put(
        "/api/reaction",
        headers=get_user_token_headers(username=user.username),
        json={"reaction_id": reaction.reaction_id},
    )
    assert response.status_code == 200
    assert response.json()["reaction"] == "dislike"


def test_delete_reaction_success(client, db_session):
    user = add_user(db_session)
    post = add_post(db_session, user_fk=user.user_id)
    reaction = add_reaction(db_session, user_fk=user.user_id, post_fk=post.post_id)
    response = client.delete(
        f"/api/reaction/{reaction.reaction_id}",
        headers=get_user_token_headers(test_data),
    )
    assert response.status_code == 200
    assert response.json() == "Реакция удалена"


def test_put_and_delete_access_error(client, db_session):
    user = add_user(db_session)
    user2 = add_user(db_session, username='test2')
    post = add_post(db_session, user_fk=user.user_id)
    reaction = add_reaction(db_session, user_fk=user.user_id, post_fk=post.post_id)
    response = client.put(
        "/api/reaction",
        headers=get_user_token_headers(username=user2.username),
        json={"reaction_id": reaction.reaction_id},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Вы не можете изменить не свою реакцию / Недостаточно прав"

    response = client.delete(
        f"/api/reaction/{reaction.reaction_id}",
        headers=get_user_token_headers(username=user2.username),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Вы не можете удалять не свою реакцию / Недостаточно прав"

