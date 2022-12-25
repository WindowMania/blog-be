import uuid
import pydantic
from enum import Enum

from src.user.unit_of_work import UserUnitOfWork
from src.user.model import UserEntity
from typing import Optional
from src.infra.auth20 import Auth20, AuthPlatform
from src.infra.jwt import JwtContext
from src.infra.hash import get_hash, verify_hash


class NotExistUserError(Exception):
    def __init__(self):
        self.message = "not exist user"


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


def login_user(uow: UserUnitOfWork, username: str, password: str):
    with uow:
        user = uow.users.find_by_account(username)
        if not user or not verify_hash(password, user.password):
            raise NotExistUserError
        return user


def login_oauth20(uow: UserUnitOfWork, jwt_ctx: JwtContext, platform: AuthPlatform, access_key: str) -> str:
    oauth_ctx = Auth20.auth(platform, access_key)
    # check client id
    with uow:
        user = uow.users.find_by_account(oauth_ctx.email)
        if not user:
            password = uuid.uuid4().hex
            UserCreateDto(account=oauth_ctx.email, password=get_hash(password), nick_name=oauth_ctx.name)
        return jwt_ctx.create_access_token({"username": oauth_ctx.email})
