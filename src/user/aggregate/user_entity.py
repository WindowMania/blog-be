from typing import Optional
from datetime import datetime
import uuid


class UserEntity:
    id: str
    account: str
    password: str
    nick_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, account: str, password: str, nick_name: Optional[str]):
        self.id = uuid.uuid4().hex
        self.account = account
        self.password = password
        self.nick_name = nick_name
