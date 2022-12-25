from typing import Optional
from sqlalchemy.orm import Session

from src.user.model import UserEntity
from src.infra.repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, UserEntity)

    def find_by_account(self, account: str) -> Optional[UserEntity]:
        return self.session.query(UserEntity) \
            .filter_by(account=account) \
            .first()
