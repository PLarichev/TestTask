from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import Users
from app.endpoints.auth import signup, OAuth2PasswordRequestForm

router = APIRouter()


class UpdateUser(BaseModel):
    """
    Модель данных для обновления пользователя.
    """
    user_id: int
    username: Optional[str]
    password: Optional[str]


@router.get('/users', response_model=list[Users])
async def get_users(session: Session = Depends(get_session)):
    """
    Получает всех пользователей.

    :param session: Сессия базы данных.
    :return: Ответ со списком пользователей
    """
    users = session.exec(select(Users)).all()
    if not users:
        raise HTTPException(detail="Не существует ни одного пользователя",
                            status_code=404)
    return users


@router.get('/users/{user_id}', response_model=Users)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """
    Получает пользователя по id.

    :param user_id: Идентификатор пользователя.
    :param session: Сессия базы данных.
    :return: Пользователь.
    """
    user = session.exec(select(Users).where(Users.user_id == user_id)).one_or_none()
    if not user:
        raise HTTPException(detail=f'Пользователь с id {user_id} не найден',
                            status_code=404)
    return user


@router.get('/users/{username}', response_model=Users)
async def get_user(username: str, session: Session = Depends(get_session)):
    """
    Получает пользователя по username.

    :param username: Имя пользователя.
    :param session: Сессия базы данных.
    :return: Пользователь.
    """
    user = session.exec(select(Users).where(Users.username == username)).one_or_none()
    if not user:
        raise HTTPException(detail=f'Пользователь с username {username} не найден',
                            status_code=404)
    return user


@router.post('/users', response_model=Users)
async def post_user(form_data: OAuth2PasswordRequestForm = Depends(),
                    session: Session = Depends(get_session)):
    """
    Регистрация нового пользователя. Код взят из app/endpoints/auth.py, чтобы сохранить принцип DRY
    """
    new_user = await signup(form_data, session)
    return new_user


@router.put('/users', response_model=Users)
async def put_user(form_data: UpdateUser,
                   session: Session = Depends(get_session)):
    """
    Обновляет данные пользователя.

    :param form_data: Данные формы получения пользователя, может содержать id или username, может отсутствовать.
    :param session: Сессия базы данных.
    :return: Обновленный пользователь.
    """
    if not form_data:
        raise HTTPException(detail='Не указан id или username пользователя',
                            status_code=400)
    user = session.exec(select(Users).where(Users.user_id == form_data.user_id)).one_or_none()
    if not user:
        raise HTTPException(detail=f'Пользователь с id {form_data.user_id} не найден',
                            status_code=404)
    user_dict = form_data.dict(exclude_unset=True)
    if user_dict.get('username'):
        same_username = session.exec(select(Users).where(Users.username == user_dict['username'])).one_or_none()
        if same_username and same_username.user_id != user.user_id:
            raise HTTPException(detail=f'Пользователь с именем {user_dict["username"]} уже существует',
                                status_code=400)
    for key, value in user_dict.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete('/users/{user_id}', response_model=list[Users])
async def delete_user(user_id: int,
                      session: Session = Depends(get_session)):
    """
    Удаляет пользователя.
    :param user_id: id пользователя для удаления
    :param session: Сессия базы данных.
    :return: Список всех пользователей
    """
    user = session.exec(select(Users).where(Users.user_id == user_id)).one_or_none()
    if not user:
        raise HTTPException(detail=f'Пользователь с id {user_id} не найден',
                            status_code=404)
    session.delete(user)
    session.commit()
    return await get_users(session)
