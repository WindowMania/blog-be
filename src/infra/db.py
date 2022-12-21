from __future__ import annotations
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infra.config import MysqlSessionConfig

logger = logging.getLogger(__name__)


def get_url():
    db_config_ = MysqlSessionConfig.get_config()
    return db_config_.get_url()


def create_engine_by_config(db_config_: MysqlSessionConfig):
    return create_engine(  # 2
        db_config_.get_url(),
        echo=True
    )


def create_session_maker(engine_, db_config_: MysqlSessionConfig):
    return sessionmaker(autocommit=db_config_.DB_AUTO_COMMIT,
                        autoflush=db_config_.DB_AUTO_FLUSH,
                        bind=engine_
                        )


def create_persistence(db_config: MysqlSessionConfig = MysqlSessionConfig.get_config()):
    engine = create_engine_by_config(db_config)
    session_maker = create_session_maker(engine, db_config)
    return engine, session_maker
