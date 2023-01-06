import pytest

from tests.fixture.session import uow
from src.infra.config import Config
from src.user.services import UserService, UserEmailService, UserAuthService
from src.infra.email import MockSmtpGmail
from src.infra.jwt import JwtContext
from src.infra.oauth import OAuthContext

conf = Config.get_config("test")


@pytest.fixture(scope="function")
def user_service(uow):
    yield UserService(uow)


@pytest.fixture(scope="function")
def user_email_service(uow):
    email_ctx = MockSmtpGmail("none", "none")
    yield UserEmailService(uow, conf, email_ctx)


@pytest.fixture(scope="function")
def user_auth_service(uow):
    jwt_ctx = JwtContext(conf.JWT_SECRET_KEY)
    oauth_ctx = OAuthContext(conf)
    yield UserAuthService(uow, jwt_ctx, oauth_ctx)
