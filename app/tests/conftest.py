import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlmodel import create_engine, Session
from app.main import app
from app.db.session import get_session
from app.core.auth import get_access_token
from app.db.models import Base, Users, Posts, Reactions


DATABASE_URL = "sqlite:///./pytest.db"
test_data = "test"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
event.listen(engine, "connect", lambda c, _: c.execute("pragma foreign_keys=on"))
Base.metadata.create_all(bind=engine)


TestingSessionLocal: Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def test_app():
    Base.metadata.create_all(engine)
    _app = app
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def get_user_token(test_user):
    return get_access_token(test_user.username)["access_token"]


def get_user_token_headers(username):
    token = get_access_token(username)
    return {"Authorization": "Bearer " + token["access_token"]}


def add_user(session: Session,
             username=test_data,
             password=test_data):
    new_user = Users(username=username, password=password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def add_post(session: Session,
             user_fk=None,
             post_content=test_data):
    new_post = Posts(user_fk=user_fk, post_content=post_content)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


def add_reaction(session: Session,
                 user_fk=None,
                 post_fk=None,
                 reaction='like'):
    new_reaction = Reactions(user_fk=user_fk, post_fk=post_fk, reaction=reaction)
    session.add(new_reaction)
    session.commit()
    session.refresh(new_reaction)
    return new_reaction

@pytest.fixture
def test_user(db_session: Session):
    return add_user(db_session)


@pytest.fixture
def user_token_headers(test_user):
    return get_user_token_headers(test_user.username)


@pytest.fixture()
def client(test_app, db_session: Session):
    def _get_test_db_session():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides[get_session] = _get_test_db_session

    with TestClient(test_app) as client:
        yield client
        test_app.dependency_overrides = {}
