from typing import Generator
from src.infra.db import create_persistence, MysqlSessionConfig
from src.infra.jwt import JwtContext
from src.infra.config import JwtConfig

engine, sessionMaker = create_persistence(MysqlSessionConfig.get_config())
jwt_config = JwtConfig.get_config()
jwt_context = JwtContext(jwt_config.JWT_SECRET_KEY)


def get_transaction() -> Generator:
    yield sessionMaker()


def get_jwt_ctx() -> JwtContext:
    return jwt_context
