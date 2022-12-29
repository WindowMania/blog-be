from typing import Generator
import pydantic
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from src.user.service import UserService, UserAuthService
from src.infra.db import create_persistence, MysqlSessionConfig
from src.infra.jwt import JwtContext
from src.infra.config import JwtConfig, OAuthConfig
from src.user.model import UserEntity
from src.user.unit_of_work import SqlAlchemyUow
from src.infra.oauth import OAuthContext

engine, sessionMaker = create_persistence(MysqlSessionConfig.get_config())
jwt_config = JwtConfig.get_config()
jwt_context = JwtContext(jwt_config.JWT_SECRET_KEY)

oauth_config = OAuthConfig.get_config()
oauth_context = OAuthContext(oauth_config)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")
uow = SqlAlchemyUow(sessionMaker)

user_service = UserService(uow)
user_auth_service = UserAuthService(uow, jwt_context, oauth_context)


async def get_user_service():
    return user_service


async def get_user_auth_service():
    return user_auth_service


async def get_jwt_ctx() -> JwtContext:
    return jwt_context


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_context.decode_token(token)
        username: str = payload.get("username")
    except Exception:
        raise credentials_exception

    with uow:
        user = uow.users.find_by_account(username)
        if user is None:
            raise credentials_exception
        uow.detach_from_persistence()
    return user
