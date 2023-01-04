from tests.fixture.session import *

from src.user.service import UserService, FailCreateUser


def test_create_validation_user(uow):
    valid_account = "test@gamil.com"
    valid_password = "1a@!xdcsd2"
    invalid_account = "바보바보"
    invalid_password = "111111111111"
    user_service = UserService(uow)
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

# def test_create_user(user_uow):
#     account = "kyb_test@gmail.com"
#     password = "test1234"
#     user_dto = user_service.UserCreateDto(account=account, password=password)
#     user_id = user_service.create_user(user_uow, user_dto)
#     assert user_id is not None
