# from src.infra.repository import SqlAlchemyRepository
from src.user.aggregate.user_entity import UserEntity
from typing import Optional
import uuid


class UserRepository:

    @staticmethod
    def add(session, model: UserEntity):
        session.add(model)

    @staticmethod
    def find_by_account(session, account: str) -> Optional[UserEntity]:
        return session.query(UserEntity) \
            .filter_by(account=account) \
            .first()

    @staticmethod
    def get(session, id_: str) -> Optional[UserEntity]:
        return session.query(UserEntity) \
            .filter_by(id=id_) \
            .first()
