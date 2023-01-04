from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from enum import Enum
from src.infra.monad import Success
from src.infra.validation import check_email
import uuid


class InvalidAccount(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidPassword(Exception):
    def __init__(self, message: str):
        self.message = message


class UserCodeAuthenticationMethod(str, Enum):
    email = "Email"
    phone = "phone"


class UserStatus(str, Enum):
    normal = "normal"
    sign = "sign"
    resign = "resign"
    block = "block"


class UserCodeAuthentication:
    id: str
    user_id: str
    method: UserCodeAuthenticationMethod
    code: str
    created_at: Optional[datetime]
    start_at: datetime
    end_at: datetime


class UserEntity:
    id: str
    account: str
    status: UserStatus
    password: str
    nick_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    code_authentication_list: List[UserCodeAuthentication]

    def __init__(self, status: UserStatus, account: str, password: str, nick_name: Optional[str]):
        self.id = uuid.uuid4().hex
        self.account = account
        self.password = password
        self.nick_name = nick_name
        self.status = status
        self.code_authentication = []

    @staticmethod
    def __check_account(user_entity: UserEntity) -> UserEntity:
        if check_email(user_entity.account):
            return user_entity
        raise InvalidAccount(message="잘못된 이메일 형식입니다.")

    @staticmethod
    def __check_password(user_entity: UserEntity) -> UserEntity:
        messages = []
        pwd = user_entity.password
        if len(pwd) < 8:
            messages.append("비밀번호 길이는 최소 8글자 이상 입니다.")
        if len(pwd) > 30:
            messages.append("비밀번호 길이는 최대 30글자 미만 입니다.")
        if not any(char.isdigit() for char in pwd):
            messages.append("비밀번호는 최소 한 글자 이상의 숫자를 포함 해야 합니다.")
        if not any(char.islower() for char in pwd):
            messages.append("비밀번호는 최소 한 글자 이상의 소문자를 포함 해야 합니다.")
        if messages:
            raise InvalidPassword(message="\n".join(messages))
        return user_entity

    def check_join(self) -> Success[UserEntity]:
        ret = Success(self) \
            .bind(UserEntity.__check_account) \
            .bind(UserEntity.__check_password)
        return ret
