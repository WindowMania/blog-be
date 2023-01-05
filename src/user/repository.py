from typing import Optional
from sqlalchemy.orm import Session, lazyload, joinedload

from src.user.models import UserEntity
from src.infra.repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, UserEntity)

    def find_by_account(self, account: str) -> Optional[UserEntity]:
        return self.session.query(UserEntity) \
            .filter_by(account=account) \
            .first()

    def find_by_account_load_authcode(self, account: str) -> Optional[UserEntity]:
        return self.session.query(UserEntity) \
            .options(joinedload(UserEntity.code_authentication_list)) \
            .filter_by(account=account) \
            .first()

    def get(self, ref) -> Optional[UserEntity]:
        return super().get(ref)
