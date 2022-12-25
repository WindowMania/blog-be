from typing import Generator
import pydantic
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

import src.user.service as user_service
from src.infra.db import create_persistence, MysqlSessionConfig
from src.infra.jwt import JwtContext
from src.infra.config import JwtConfig
from src.user.model import UserEntity
from src.user.unit_of_work import UserUnitOfWork

engine, sessionMaker = create_persistence(MysqlSessionConfig.get_config())
jwt_config = JwtConfig.get_config()
jwt_context = JwtContext(jwt_config.JWT_SECRET_KEY)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")
user_unit_of_work = UserUnitOfWork(sessionMaker)


async def get_jwt_ctx() -> JwtContext:
    return jwt_context


async def get_user_uow() -> UserUnitOfWork:
    return user_unit_of_work


class UserRes(pydantic.BaseModel):
    account: str


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

    with user_unit_of_work:
        user = user_unit_of_work.users.find_by_account(username)
        if user is None:
            raise credentials_exception
        return UserRes(account=user.account)
