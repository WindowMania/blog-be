from __future__ import annotations
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infra.config import Config
from src.infra.orm import metadata
logger = logging.getLogger(__name__)


def get_url():
    db_config_ = Config.get_config()
    return db_config_.get_db_url()


def create_engine_by_config(db_config_: Config):
    return create_engine(  # 2
        db_config_.get_db_url(),
        echo=True
    )


def create_session_maker(engine_, db_config_: Config):
    return sessionmaker(autocommit=db_config_.DB_AUTO_COMMIT,
                        autoflush=db_config_.DB_AUTO_FLUSH,
                        bind=engine_
                        )


def create_persistence(db_config: Config = Config.get_config()):
    engine = create_engine_by_config(db_config)
    session_maker = create_session_maker(engine, db_config)
    return engine, session_maker


def truncate(engine):
    engine_name = engine.name
    with engine.begin() as conn:
        if engine_name == 'mysql':
            conn.execute('SET FOREIGN_KEY_CHECKS=0;')
        elif engine_name == 'postgresql':
            conn.execute('SET CONSTRAINTS ALL DEFERRED;')
        elif engine_name == 'sqlite':
            conn.execute('PRAGMA foreign_keys = OFF;')

        for table in reversed(metadata.sorted_tables):
            if engine_name == 'mysql':
                conn.execute('TRUNCATE TABLE {};'.format(table.name))
            elif engine_name == 'postgresql':
                conn.execute('TRUNCATE TABLE {} RESTART IDENTITY CASCADE;'.format(table.name))
            elif engine_name == 'sqlite':
                conn.execute('DELETE FROM {};'.format(table.name))

        if engine_name == 'mysql':
            conn.execute('SET FOREIGN_KEY_CHECKS=1;')
        elif engine_name == 'postgresql':
            conn.execute('SET CONSTRAINTS ALL IMMEDIATE;')
        elif engine_name == 'sqlite':
            conn.execute('PRAGMA foreign_keys = ON;')