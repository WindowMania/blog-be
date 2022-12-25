import pytest

from tests.fixture.session import *
from src.user.repository.user import UserRepository
from src.user.aggregate.user_entity import UserEntity


def test_create_user(session):
    account = "kyb_test@gmail.com"
    password = "test1234"
    user = UserEntity(account=account, password=password, nick_name="test")
    UserRepository.add(session, user)
    session.flush()
    persistence_user = UserRepository.get(session, user.id)
    assert persistence_user.id == user.id
    assert persistence_user.account == account
    assert persistence_user.password == password


