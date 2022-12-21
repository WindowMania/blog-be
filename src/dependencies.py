from typing import Generator
from src.infra.db import create_persistence, MysqlSessionConfig

engine, sessionMaker = create_persistence(MysqlSessionConfig.get_config())


def get_transaction() -> Generator:
    yield sessionMaker()
