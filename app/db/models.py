from sqlmodel import SQLModel, Field
from typing import Optional


class Base(SQLModel):
    pass


class Users(Base, SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str


class Posts(Base, SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, primary_key=True)
    user_fk: int = Field(foreign_key='users.user_id')
    post_content: str


class Reactions(Base, SQLModel, table=True):
    reaction_id: Optional[int] = Field(default=None, primary_key=True)
    post_fk: int = Field(foreign_key='posts.post_id')
    user_fk: int = Field(foreign_key='users.user_id')
    reaction: str = 'like|dislike'


