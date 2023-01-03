from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


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

    def __init__(self, status: UserStatus, account: str, password: str, nick_name: Optional[str]):
        self.id = uuid.uuid4().hex
        self.account = account
        self.password = password
        self.nick_name = nick_name
        self.status = status
