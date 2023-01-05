from __future__ import annotations
from pydantic import BaseSettings
from dotenv import load_dotenv, find_dotenv
from typing import NewType, Literal, TypeVar, Generic

load_dotenv(find_dotenv(filename=".env"))

AppMode = NewType("AppMode", Literal["dev", "test", "prod"])
T = TypeVar('T')


class AppConfig(BaseSettings):
    APP_MODE: AppMode = "dev"


app_config = AppConfig()


class Config(BaseSettings):
    # [ DB ]
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_ADDRESS: str = '127.0.0.1'
    DATABASE_NAME: str
    DB_AUTO_COMMIT: bool = False
    DB_AUTO_FLUSH: bool = False

    # [ JWT ]
    JWT_SECRET_KEY: str

    # [ OAuth ]
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # [ Domain ]
    DOMAIN_ROOT: str
    DOMAIN_BACKEND: str
    DOMAIN_FRONTEND: str

    # [ URL ]
    JOIN_VERIFY_URL: str

    # [ GMAIL ]
    GMAIL_ACCOUNT: str
    GMAIL_PASSWORD: str

    @staticmethod
    def get_app_config() -> AppConfig:
        return app_config

    @staticmethod
    def get_config(app_mode: AppMode = app_config.APP_MODE) -> Config:
        load_dotenv(find_dotenv(filename=f".env.{app_mode}"), override=True)
        return Config()

    def get_db_url(self):
        return f"mysql+pymysql://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@" \
               f"{self.DATABASE_ADDRESS}/{self.DATABASE_NAME}"

