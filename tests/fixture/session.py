import pytest

from src.infra.config import MysqlSessionConfig
from src.infra.db import create_persistence, truncate
from migrate import Migrate
from src.infra.orm import start_mappers
from tests.mock.user_uow import MockSqlAlchemyUow


@pytest.fixture(scope="session")
def db():
    start_mappers()
    app_mode = 'test'
    db_config = MysqlSessionConfig.get_config(app_mode)
    engine, session_maker = create_persistence(db_config)
    _db = {
        "engine": engine,
        "session_maker": session_maker
    }
    Migrate.upgrade(app_mode)
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
    # truncate(db['engine'])
