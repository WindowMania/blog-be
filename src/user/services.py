import uuid
import pydantic

from src.user.unit_of_work import SqlAlchemyUow
from src.user.models import UserEntity, UserStatus, FailUserLogin
from src.infra.jwt import JwtContext, JwtToken
from src.infra.oauth import OAuthPlatform, OAuthContext
from src.infra.email import EmailContext
from src.infra.config import Config
from src.infra.hash import get_hash, verify_hash


class NotExistUserError(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 유저"


class FailCreateUser(Exception):
    def __init__(self, message):
        self.message = message


class UserDto(pydantic.BaseModel):
    account: str
    nick_name: str


class CreateUserResult(pydantic.BaseModel):
    user_id: str


class UserService:
    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def create_user(self, email: str, password: str, nick_name: str = "noname") -> CreateUserResult:
        with self.uow:
            user = self.uow.users.find_by_account(account=email)
            if user:
                raise FailCreateUser("이미 존재 하는 유저")
            new_user_entity = UserEntity(account=email,
                                         status=UserStatus.sign,
                                         password=password,
                                         nick_name=nick_name)
            result = new_user_entity.validate_join()
            if not result:
                raise FailCreateUser(result.get_error_message())
            new_user_entity.set_hash_password(get_hash(password))
            self.uow.users.add(new_user_entity)
            self.uow.commit()
            return CreateUserResult(user_id=new_user_entity.id)


class UserEmailService:
    def __init__(self, uow: SqlAlchemyUow,
                 conf: Config,
                 email_ctx: EmailContext,
                 ):
        self.uow = uow
        self.email_ctx = email_ctx
        self.conf = conf

    def send_join_verify_email(self, user_account: str) -> str:
        with self.uow:
            user = self.uow.users.find_by_account(account=user_account)
            if not user:
                raise NotExistUserError()
            auth_code = user.add_code_authentication()
            self.uow.users.add(user)
            self.uow.commit()
            title = "회원가입 인증 메일 입니다."
            q = f"?code={auth_code}&user_account={user_account}"
            message = self.conf.DOMAIN_FRONTEND + self.conf.JOIN_VERIFY_URL + q
            self.email_ctx.send_simple_text_email(user_account, title, message)
            return auth_code


class UserAuthService:
    def __init__(self, uow: SqlAlchemyUow, jwt_ctx: JwtContext, oauth_ctx: OAuthContext):
        self.uow = uow
        self.jwt_ctx = jwt_ctx
        self.oauth_ctx = oauth_ctx

    def login_by_password(self, account: str, password: str) -> JwtToken:
        with self.uow:
            user = self.uow.users.find_by_account(account)
            if not user:
                raise NotExistUserError()
            if not verify_hash(password, user.password):
                raise FailUserLogin("잘못된 유저 정보")
            user.check_possible_login()
            return self.jwt_ctx.create_access_token({"username": user.account})

    def reauthorize_by_oauth(self, code: str, platform: OAuthPlatform) -> JwtToken:
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

    def join_verify(self, account: str, code: str):
        with self.uow:
            user = self.uow.users.find_by_account_load_authcode(account=account)
            if not user:
                raise NotExistUserError()
            user.validate_authentication_code(code=code)
            user.status = UserStatus.normal
            self.uow.users.add(user)
            self.uow.commit()
