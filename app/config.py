from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    PROJECT_NAME: str = "TestTask"
    SECRET_KEY: str = "2c$13$ISILTUMkl6kpnF3vC5zQt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    DATABASE_URL: str = "sqlite:///./test.db"


config = Settings()
