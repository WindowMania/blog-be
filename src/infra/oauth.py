import abc
from enum import Enum

import json

import pydantic
import requests

from src.infra.config import OAuthConfig


class OAuthError(Exception):
    def __init__(self, message):
        self.message = message


class OAuthPlatform(str, Enum):
    google = "google"
    github = "github"


class OAuthResponse(pydantic.BaseModel):
    email: str
    nick_name: str


class OAuth:
    def __init__(self, platform: OAuthPlatform, client_id: str, client_secret: str):
        self.platform = platform
        self.client_secret = client_secret
        self.client_id = client_id

    @abc.abstractmethod
    def get_access_key(self, code: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_oauth_response(self, access_key) -> OAuthResponse:
        raise NotImplementedError

    def is_platform(self, p: OAuthPlatform):
        if self.platform == p:
            return True
        return False


class GithubOAuth(OAuth):
    def get_access_key(self, code: str) -> str:
        URL = "https://github.com/login/oauth/access_token"
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            "Accept": "application/json"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        response = requests.post(URL, headers=headers, data=json.dumps(data))
        if not response.ok:
            raise OAuthError("github get access_key fail")
        result = response.json()
        return result["access_token"]

    def get_oauth_response(self, access_key) -> OAuthResponse:
        URL = "https://api.github.com/user"
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            "Accept": "application/json",
            "Authorization": f"Bearer {access_key}"
        }
        response = requests.get(URL, headers=headers)
        if not response.ok:
            raise OAuthError("github get user fail")
        result = response.json()
        return OAuthResponse(email=result['email'], nick_name=result['name'])


class GoogleOAuth(OAuth):

    def get_access_key(self, code: str) -> str:
        URL = "https://oauth2.googleapis.com/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            # "Accept": "application/json"
        }
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": f"http://localhost:3000/callback?platform=google"
        }
        response = requests.post(URL, headers=headers, data=data)
        if not response.ok:
            raise OAuthError("google get access_key fail")
        result = response.json()
        return result["access_token"]

    def get_oauth_response(self, access_key) -> OAuthResponse:
        URL = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_key}'
        headers = {
            "Authorization": f'token {access_key}',
            "Accept": "application/json",
        }
        response = requests.get(URL, headers=headers)
        if not response.ok:
            raise OAuthError("google get user fail")
        result = response.json()

        return OAuthResponse(email=result['email'], nick_name=result['name'])


class OAuthContext:

    def __init__(self, config: OAuthConfig):
        self.config = config
        self.oauth_list = [
            GithubOAuth(OAuthPlatform.github, config.GITHUB_CLIENT_ID, config.GITHUB_CLIENT_SECRET),
            GoogleOAuth(OAuthPlatform.google, config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET)
        ]

    def get_access_key(self, platform: OAuthPlatform, code: str):
        for o in self.oauth_list:
            if o.is_platform(platform):
                return o.get_access_key(code)

    def get_oauth_response(self, platform: OAuthPlatform, access_key: str) -> OAuthResponse:
        for o in self.oauth_list:
            if o.is_platform(platform):
                return o.get_oauth_response(access_key)
