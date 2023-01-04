import uuid
import pydantic

from src.user.unit_of_work import SqlAlchemyUow
from src.user.models import UserEntity, UserStatus
from typing import Optional

from src.infra.jwt import JwtContext
from src.infra.oauth import OAuthPlatform
from src.infra.oauth import OAuthContext

from src.infra.hash import get_hash, verify_hash


class NotExistUserError(Exception):
    def __init__(self):
        self.message = "not exist user"


class FailCreateUser(Exception):
    def __init__(self, message):
        self.message = message


class UserDto(pydantic.BaseModel):
    account: str
    nick_name: str


# def create_user(uow: SqlAlchemyUow, create_dto: UserCreateDto):
#     # dto 검사..
#     # 이미 있는지 확인
#     with uow:
#         new_user_entity = UserEntity(**create_dto.dict())
#         uow.users.add(new_user_entity)
#         uow.commit()
#         return new_user_entity.id
#     # 생성 실패..
#
#
# def login_user(uow: SqlAlchemyUow, username: str, password: str):
#     with uow:
#         user = uow.users.find_by_account(username)
#         if not user or not verify_hash(password, user.password):
#             raise NotExistUserError
#         return user
#
#
# def reauthorize(uow: SqlAlchemyUow, jwt_ctx: JwtContext, platform: AuthPlatform, access_key: str) -> str:
#     oauth_ctx = Auth20.auth(platform, access_key)
#     # check client id
#     with uow:
#         user = uow.users.find_by_account(oauth_ctx.email)
#         if not user:
#             password = uuid.uuid4().hex
#             UserCreateDto(account=oauth_ctx.email, password=get_hash(password), nick_name=oauth_ctx.name)
#         return jwt_ctx.create_access_token({"username": oauth_ctx.email})
#

class UserService:
    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def create_user(self, email: str, password: str, nick_name: str = "noname") -> str:

        with self.uow:
            user = self.uow.users.find_by_account(account=email)
            if user:
                raise FailCreateUser("이미 존재 하는 유저")

            new_user_entity = UserEntity(account=email, status=UserStatus.sign, password=password, nick_name=nick_name)
            result = new_user_entity.check_join()
            if not result:
                raise FailCreateUser(result.get_error_message())
            self.uow.users.add(new_user_entity)
            self.uow.commit()
            return new_user_entity.id


class UserAuthService:
    def __init__(self, uow: SqlAlchemyUow, jwt_ctx: JwtContext, oauth_ctx: OAuthContext):
        self.uow = uow
        self.jwt_ctx = jwt_ctx
        self.oauth_ctx = oauth_ctx

    def login_by_password(self):
        pass

    def reauthorize_by_oauth(self, code: str, platform: OAuthPlatform):
        access_key = self.oauth_ctx.get_access_key(platform, code)
        oauth_res = self.oauth_ctx.get_oauth_response(platform, access_key)
        with self.uow:
            user = self.uow.users.find_by_account(oauth_res.email)
            if not user:
                new_user_entity = UserEntity(status=UserStatus.normal,
                                             account=oauth_res.email,
                                             password=uuid.uuid4().hex,
                                             nick_name=oauth_res.nick_name)
                self.uow.users.add(new_user_entity)
                self.uow.commit()
            return self.jwt_ctx.create_access_token({"username": oauth_res.email})
