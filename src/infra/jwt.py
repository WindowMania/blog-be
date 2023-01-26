from typing import Optional, Dict
from datetime import datetime, timedelta

from jose import JWTError, jwt


class JwtTimeoutError(Exception):
    def __init__(self):
        self.message = "jwt timeout"


class JwtValidationError(Exception):
    def __init__(self):
        self.message = "jwt validation"


class JwtToken:

    def __init__(self,
                 access_key: str,
                 exp: datetime
                 ):
        self.access_key = access_key
        self.exp = exp


class JwtContext:

    def __init__(self, secret_key: str, algorithm: str = "HS256", expire=300):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire = expire

    def _get_default_expire(self):
        return timedelta(minutes=self.expire)

    def create_access_token(self, data: dict, expire_delta: Optional[timedelta] = None) -> JwtToken:
        to_encode = data.copy()
        expire = datetime.utcnow() + self._get_default_expire()
        if expire_delta and expire_delta > 0:
            expire = datetime.utcnow() + expire_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return JwtToken(access_key=encoded_jwt, exp=expire)

    def decode_token(self, access_token: str) -> Dict[str, str]:
        try:
            payload = jwt.decode(access_token, self.secret_key, self.algorithm)
            if datetime.fromtimestamp(payload['exp']) < datetime.now():
                raise JwtTimeoutError
            return payload
        except JWTError:
            raise JwtValidationError
