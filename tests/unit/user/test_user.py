from tests.fixture.session import *

from src.user.repository import UserRepository
from src.user.model import UserEntity
import src.user.service as user_service
from src.user.unit_of_work import UserUnitOfWork


def test_create_user(user_uow):
    account = "kyb_test@gmail.com"
    password = "test1234"
    user_dto = user_service.UserCreateDto(account=account, password=password)
    user_id = user_service.create_user(user_uow, user_dto)
    assert user_id is not None
