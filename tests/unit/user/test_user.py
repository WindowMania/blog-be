import time

from tests.fixture.session import *

from src.user.services import FailCreateUser
from tests.fixture.user_services import user_service, user_email_service, user_auth_service


def test_create_validation_user(user_service):
    valid_account = "test@gamil.com"
    valid_password = "1a@!xdcsd2"
    invalid_account = "바보바보"
    invalid_password = "111111111111"
    # 잘못된 비밀번호.
    with pytest.raises(FailCreateUser):
        user_service.create_user(email=valid_account, password=invalid_password)
    # 잘못된 계정
    with pytest.raises(FailCreateUser):
        user_service.create_user(email=invalid_account, password=valid_password)

    user_service.create_user(email=valid_account, password=valid_password)
    # # 중복 계정 생성
    with pytest.raises(FailCreateUser):
        user_service.create_user(email=valid_account, password=valid_password)


def test_join_validation(user_service, user_email_service, user_auth_service):
    account = "test@gmail.com"
    password = "1q2w3e4r1!"
    user_service.create_user(account, password)
    code = user_email_service.send_join_verify_email(account)
    user_auth_service.join_verify(account, code)
