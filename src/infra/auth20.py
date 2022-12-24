from enum import Enum
from typing import Optional

import pydantic
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token


class AuthPlatform(str, Enum):
    google = "google"


class AuthResult(pydantic.BaseModel):
    client_id: str
    email: str
    iss: str
    name: Optional[str]


class Auth20:
    @staticmethod
    def auth_google(token: str):
        account_info = verify_oauth2_token(token, requests.Request())
        client_id = account_info['aud']
        email = account_info['email']
        iss = account_info['iss']
        name = account_info['name']
        return AuthResult(client_id=client_id, email=email, iss=iss, name=name)

    @staticmethod
    def auth(target: AuthPlatform, token: str) -> AuthResult:
        if target == AuthPlatform.google:
            return Auth20.auth_google(token)
