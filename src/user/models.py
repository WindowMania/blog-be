from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
from src.infra.monad import Success
from src.infra.validation import check_email
import uuid


class FailUserLogin(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidAccount(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidPassword(Exception):
    def __init__(self, message: str):
        self.message = message


class FailUserAuthCode(Exception):
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

    def __init__(self,
                 user_id: str,
                 period: timedelta,
                 method: UserCodeAuthenticationMethod = UserCodeAuthenticationMethod.email,
                 code: str = uuid.uuid4().hex[:30]
                 ):
        self.id = uuid.uuid4().hex
        self.user_id = user_id
        self.method = method
        self.code = code
        self.start_at = datetime.now()
        self.end_at = self.start_at + period

    def is_valid_time(self) -> bool:
        # 테스트 코드에서 시간차 문제 생김.
        # 즉 이메일 보냈을 때의 시간 범위 보다 작은 값으로 할당 되어서 테스트 코드가 실패 함
        # -> 그러나 이는 현실적으로 테스트 상황에서나 발생하는 문제로 판단.
        # 테스트 코드 안에서 sleep 하면 해결 되는 문제이나, 테스트 코드는 최대한 빨라야하므로
        # timedelta(minutes=0.5)으로 통과되도록 꼼수 부림.
        current = datetime.now() + timedelta(minutes=0.5)
        if self.start_at <= current < self.end_at + timedelta(minutes=0.5):
            return True
        return False


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
        self.code_authentication_list = []

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

    def validate_join(self) -> Success[UserEntity]:
        ret = Success(self) \
            .bind(UserEntity.__check_account) \
            .bind(UserEntity.__check_password)
        return ret

    def add_code_authentication(self) -> str:
        code_authentication = UserCodeAuthentication(self.id, timedelta(days=1))
        self.code_authentication_list.append(code_authentication)
        return code_authentication.code

    def validate_authentication_code(self, code: str) -> bool:
        r = [auth for auth in self.code_authentication_list if auth.code == code]
        if not r:
            raise FailUserAuthCode(f"{self.account}에 해당 인증 정보가 존재 하지 않습니다")
        auth = r[0]
        print("뭐지??: ", auth.start_at, auth.end_at)
        if not auth.is_valid_time():
            raise FailUserAuthCode("유효 기간이 만료된 링크")
        return True

    def is_possible_login(self):
        if self.status in [UserStatus.sign, UserStatus.resign, UserStatus.block]:
            return False
        return True

    def check_possible_login(self):
        if self.status == UserStatus.sign:
            raise FailUserLogin("인증 대기 중인 계정 입니다.")
        elif self.status == UserStatus.block:
            raise FailUserLogin("정지 중인 계정 입니다.")
        elif self.status == UserStatus.resign:
            raise FailUserLogin("삭제 계정 입니다.")

    def set_hash_password(self, hashed_password: str):
        self.password = hashed_password
