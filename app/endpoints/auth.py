from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import Users
from app.core.auth import get_access_token


router = APIRouter()


class Token(BaseModel):
    """
    Модель данных для токена доступа.
    """
    access_token: str
    token_type: str


class OAuth2PasswordRequestForm:
    """
    Модель данных для формы запроса OAuth2 пароля.
    """
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
    ):
        self.username = username
        self.password = password


@router.post('/signup', response_model=Users)
async def signup(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    """
    Регистрация нового пользователя.

    :param form_data: Данные формы запроса OAuth2 пароля.
    :param session: Сессия базы данных.
    :return: Зарегистрированный пользователь.
    """
    user_in_db = session.exec(select(Users)
                              .where(Users.username == form_data.username)
                              ).one_or_none()
    if user_in_db:
        raise HTTPException(detail='Пользователь с таким именем уже существует',
                            status_code=403)
    new_user = Users(username=form_data.username, password=form_data.password)
    session.add(new_user)
    session.commit()

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Аутентификация пользователя.

    :param form_data: Данные формы запроса OAuth2 пароля.
    :param session: Сессия базы данных.
    :return: Токен доступа.
    """

    user_in_db = session.exec(select(Users)
                              .where(Users.username == form_data.username)
                              ).one_or_none()
    if not user_in_db or user_in_db.password != form_data.password:
        raise HTTPException(detail='Некорректный логин или пароль',
                            status_code=401)

    return get_access_token(form_data.username)
