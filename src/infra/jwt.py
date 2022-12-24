from typing import Optional, Dict
from datetime import datetime, timedelta

from jose import JWTError, jwt


class JwtContext:

    def __init__(self, secret_key: str, algorithm: str = "HS256", expire=30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire = expire

    def _get_default_expire(self):
        return timedelta(minutes=self.expire)

    def create_access_token(self, data: dict, expire_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self._get_default_expire()
        if expire_delta and expire_delta > 0:
            expire = datetime.utcnow() + expire_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, str]:
        try:
            payload = jwt.decode(token, self.secret_key, self.algorithm)
            return payload
        except JWTError:
            raise JWTError
