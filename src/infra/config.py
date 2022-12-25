from __future__ import annotations
from pydantic import BaseSettings
from dotenv import load_dotenv, find_dotenv
from typing import NewType, Literal

load_dotenv(find_dotenv(filename=".env"))
AppMode = NewType("AppMode", Literal["dev", "test", "prod"])


class AppConfig(BaseSettings):
    APP_MODE: AppMode = "dev"


app_config = AppConfig()


class Config:
    @staticmethod
    def get_app_config() -> AppConfig:
        return app_config

    @staticmethod
    def load_mode(app_mode: AppMode = app_config.APP_MODE):
        load_dotenv(find_dotenv(filename=f".env.{app_mode}"), override=True)


class MysqlSessionConfig(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_ADDRESS: str = '127.0.0.1'
    DATABASE_NAME: str

    DB_AUTO_COMMIT: bool = False
    DB_AUTO_FLUSH: bool = False

    @staticmethod
    def get_config(app_mode: AppMode = app_config.APP_MODE) -> MysqlSessionConfig:
        Config.load_mode(app_mode)
        return MysqlSessionConfig()

    def get_url(self):
        return f"mysql+pymysql://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@" \
               f"{self.DATABASE_ADDRESS}/{self.DATABASE_NAME}"


class JwtConfig(BaseSettings):
    JWT_SECRET_KEY: str

    @staticmethod
    def get_config(app_mode: AppMode = app_config.APP_MODE) -> JwtConfig:
        Config.load_mode(app_mode)
        return JwtConfig()
