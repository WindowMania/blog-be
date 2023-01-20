from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from src.user.services import UserService, UserAuthService, UserEmailService
from src.infra.db import create_persistence
from src.infra.jwt import JwtContext
from src.infra.config import Config
from src.unit_of_work import SqlAlchemyUow
from src.infra.oauth import OAuthContext
from src.infra.email import MockSmtpGmail
from src.post.services import PostService, PostTestService

conf = Config.get_config()

engine, sessionMaker = create_persistence(conf)

jwt_context = JwtContext(conf.JWT_SECRET_KEY)
oauth_context = OAuthContext(conf)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")
uow = SqlAlchemyUow(sessionMaker)

user_service = UserService(uow)
user_auth_service = UserAuthService(uow, jwt_context, oauth_context)
user_email_service = UserEmailService(uow, conf, MockSmtpGmail(conf.GMAIL_ACCOUNT, conf.GMAIL_PASSWORD))
post_service = PostService(uow)
post_test_service = PostTestService(uow)


async def get_user_service():
    return user_service


async def get_post_test_service() -> PostTestService:
    return post_test_service


async def get_post_service():
    return post_service


async def get_user_email_service():
    return user_email_service


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
