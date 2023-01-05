from src.infra.config import Config, AppMode
from alembic.command import upgrade as alembic_upgrade, downgrade as alembic_downgrade
from alembic.config import Config as AlembicConfig
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Migrate:
    @staticmethod
    def __setting(app_mode: AppMode) -> AlembicConfig:
        logger.info(f"migrate mode: {app_mode}")
        db_config = Config.get_config(app_mode)
        alembic_config = AlembicConfig('./alembic.ini')
        alembic_config.set_main_option('sqlalchemy.url', db_config.get_db_url())
        return alembic_config

    @staticmethod
    def upgrade(app_mode: AppMode):
        conf = Migrate.__setting(app_mode)
        alembic_upgrade(conf, 'head')

    @staticmethod
    def downgrade(app_mode: AppMode):
        conf = Migrate.__setting(app_mode)
        alembic_downgrade(conf, '-1')


def select_app_mode() -> Optional[AppMode]:
    app_mode_ = input('select [test, dev, prod]: ')
    if app_mode_ in ["test", "dev", "prod"]:
        return app_mode_
    return None


if __name__ == "__main__":
    """
     이 파일을 메인으로 실행 시키면 자유롭게 마이그레이션 가능하도록
    """
    app_mode = select_app_mode()
    if app_mode:
        method = input('select up , down: ')
        if method == 'up':
            Migrate.upgrade(app_mode)
        elif method == 'down':
            Migrate.downgrade(app_mode)
