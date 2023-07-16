from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select, Session
from app.db.models import Users
from app.db.session import get_session
from app.config import config

oauth2_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Генерирует JWT-токен доступа на основе переданных данных.

    :param data: Данные, которые будут включены в токен.
    :param expires_delta: Дополнительный параметр для установки срока действия токена.
    :return: Сгенерированный токен доступа.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt


def get_access_token(username: str):
    """
    Генерирует токен доступа для указанного имени пользователя.

    :param username: Имя пользователя.
    :return: Токен доступа.
    """
    access_token = create_access_token(
        {"sub": username},
        expires_delta=timedelta(hours=config.ACCESS_TOKEN_EXPIRE_HOURS),
    )

    return {"access_token": access_token, "token_type": "bearer"}


def check_token(token: str, session: Session):
    """
    Проверяет переданный токен и возвращает соответствующего пользователя, если токен действителен.

    :param token: Токен доступа.
    :param session: Сессия базы данных.
    :return: Пользователь, если токен действителен, в противном случае False.
    """
    try:
        username: str = jwt.decode(token, config.SECRET_KEY).get("sub")
        if username is None:
            return False

        user = session.exec(select(Users)
                            .where(Users.username == username)
                            ).one_or_none()
        if not user:
            return False

        return user
    except Exception:
        return False


async def get_current_user(
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    """
    Получает текущего аутентифицированного пользователя на основе переданного токена.

    :param session: Сессия базы данных.
    :param token: Токен авторизации.
    :return: Текущий аутентифицированный пользователь.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        raw_token = token.credentials.replace("Bearer ", "")
        user = check_token(raw_token, session)
        if not user:
            raise credentials_exception

        return user
    except JWTError as exc:
        raise credentials_exception from exc