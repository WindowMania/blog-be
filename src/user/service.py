from enum import Enum

import pydantic

from src.user.unit_of_work import UserUnitOfWork
from src.user.model import UserEntity
from typing import Optional
from src.infra.auth20 import Auth20, AuthPlatform
from src.infra.jwt import JwtContext


class UserCreateDto(pydantic.BaseModel):
    account: str
    password: str
    nick_name: Optional[str]


class UserDto(pydantic.BaseModel):
    account: str
    nick_name: str


class Oauth20Platform(str, Enum):
    Google = "Google"
    Github = "Github"


def create_user(uow: UserUnitOfWork, create_dto: UserCreateDto):
    # dto 검사..
    # 이미 있는지 확인
    with uow:
        new_user_entity = UserEntity(**create_dto.dict())
        uow.users.add(new_user_entity)
        uow.commit()
        return new_user_entity.id
    # 생성 실패..


def login_oauth20(uow: UserUnitOfWork, jwt_ctx: JwtContext, platform: AuthPlatform, access_key: str) -> str:
    oauth_ctx = Auth20.auth(platform, access_key)
    # check client id

    with uow:
        user = uow.users.find_by_account(oauth_ctx.email)
        if not user:
            create_dto = UserCreateDto(account=oauth_ctx.email, nick_name=oauth_ctx.name)
            user_id = create_user(uow, create_dto)
        else:
            user_id = user.id
        return jwt_ctx.create_access_token({"user_id": user_id})


def current_user(uow: UserUnitOfWork, jwt_ctx: JwtContext, token: str) -> Optional[UserDto]:
    user_id = jwt_ctx.decode_token(token)

    with uow:
        user = uow.users.get(user_id)
        if not user:
            return None
        return UserDto(account=user.account, nick_name=user.nick_name)
