from src.infra.repository import SqlAlchemyRepository
from src.user.aggregate.user import User
from typing import Optional


class UserRepository(SqlAlchemyRepository[int, User]):

    @staticmethod
    def find_by_account(session, account: str) -> Optional[User]:
        return session.query(User) \
            .filter_by(account=account) \
            .first()