from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import Posts, Users
from app.core.auth import get_current_user

router = APIRouter()


class PostsFormData(BaseModel):
    """
    Модель данных для формы публикации.
    """
    post_id: Optional[int]
    post_content: Optional[str]


class PostsResponse(BaseModel):
    """
    Модель данных для ответа с публикациями.
    """
    posts: list[Posts]


@router.get('/posts', response_model=PostsResponse)
async def get_posts(session: Session = Depends(get_session)):
    """
    Получает все публикации.

    :param session: Сессия базы данных.
    :return: Ответ с публикациями.
    """
    posts = session.exec(select(Posts)).all()
    if not posts:
        raise HTTPException(detail='Не существует ни одной публикации',
                            status_code=404)
    return PostsResponse(posts=posts)


@router.post('/posts', response_model=Posts)
async def post_posts(form_data: PostsFormData,
                     session: Session = Depends(get_session),
                     user: Users = Depends(get_current_user)):
    """
    Создает новую публикацию.

    :param form_data: Данные формы публикации.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Созданная публикация.
    """
    new_post = Posts(user_fk=user.user_id, post_content=form_data.post_content)
    session.add(new_post)
    session.commit()
    return new_post


@router.put('/posts', response_model=Posts)
async def put_posts(form_data: PostsFormData,
                    session: Session = Depends(get_session),
                    user: Users = Depends(get_current_user)):
    """
    Изменяет существующую публикацию.

    :param form_data: Данные формы публикации.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Измененная публикация.
    """
    edited_post = session.exec(select(Posts).where(Posts.post_id == form_data.post_id)).one_or_none()
    if not edited_post:
        raise HTTPException(detail='Не найдено ни одной публикации с данным id',
                            status_code=404)
    if edited_post.user_fk != user.user_id:
        raise HTTPException(detail='Вы не можете редактировать не свой пост / Не хватает прав на редактирование',
                            status_code=403)
    edited_post.post_content = form_data.post_content
    session.add(edited_post)
    session.commit()
    session.refresh(edited_post)
    return edited_post


@router.delete('/posts/{post_id}', response_model=PostsResponse)
async def delete_posts(post_id: int,
                       session: Session = Depends(get_session),
                       user: Users = Depends(get_current_user)):
    """
    Удаляет существующую публикацию.

    :param post_id: Идентификатор публикации.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Ответ с обновленным списком публикаций.
    """
    deleted_post = session.exec(select(Posts).where(Posts.post_id == post_id)).one_or_none()
    if not deleted_post:
        raise HTTPException(detail='Не найдено ни одной публикации с данным id',
                            status_code=404)
    if deleted_post.user_fk != user.user_id:
        raise HTTPException(detail='Вы не можете удалить не свой пост / Не хватает прав на редактирование',
                            status_code=403)
    session.delete(deleted_post)
    session.commit()
    posts = session.exec(select(Posts)).all()
    return PostsResponse(posts=posts)

