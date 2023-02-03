import pytest

from src.infra.config import Config
from src.infra.db import create_persistence, truncate
from migrate import Migrate
from src.infra.orm import start_mappers
from tests.mock.uow import MockSqlAlchemyUow

from src.user.services import UserService, UserEmailService, UserAuthService
from src.infra.email import MockSmtpGmail
from src.infra.jwt import JwtContext
from src.infra.oauth import OAuthContext
from src.post.services import PostService, SeriesService

conf = Config.get_config("test")


@pytest.fixture(scope="session")
def db():
    start_mappers()
    engine, session_maker = create_persistence(conf)
    _db = {
        "engine": engine,
        "session_maker": session_maker
    }
    Migrate.upgrade('test')
    yield _db
    engine.dispose()


@pytest.fixture(scope="function")
def session(db):
    session_maker = db['session_maker']
    session = session_maker()
    yield session
    session.close()


@pytest.fixture(scope="function")
def uow(db):
    session_maker = db['session_maker']
    uow__ = MockSqlAlchemyUow(session_maker)
    yield uow__
    truncate(db['engine'])


@pytest.fixture(scope="function")
def user_service(uow):
    yield UserService(uow)


@pytest.fixture(scope="function")
def user_email_service(uow):
    email_ctx = MockSmtpGmail("none", "none")
    yield UserEmailService(uow, conf, email_ctx)


@pytest.fixture(scope="function")
def user_auth_service(uow):
    jwt_ctx = JwtContext(conf.JWT_SECRET_KEY)
    oauth_ctx = OAuthContext(conf)
    yield UserAuthService(uow, jwt_ctx, oauth_ctx)


@pytest.fixture(scope="function")
def post_service(uow):
    yield PostService(uow)


@pytest.fixture(scope="function")
def series_service(uow):
    yield SeriesService(uow)
