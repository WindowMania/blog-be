import pydantic

from src.user.unit_of_work import UserUnitOfWork
from src.user.model import UserEntity
from typing import Optional


class UserCreateDto(pydantic.BaseModel):
    account: str
    password: str
    nick_name: Optional[str]


def create_user(uow: UserUnitOfWork, create_dto: UserCreateDto):
    # dto 검사..
    with uow:
        new_user_entity = UserEntity(**create_dto.dict())
        uow.users.add(new_user_entity)
        uow.commit()
        return new_user_entity.id
    # 생성 실패..
