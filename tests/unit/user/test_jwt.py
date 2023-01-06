import pytest

from src.infra.jwt import JwtContext, JwtTimeoutError


def test_jwt():
    jwt_ctx = JwtContext("test")
    data = {"name": "kyb"}
    jwt_token = jwt_ctx.create_access_token(data)
    decode_data = jwt_ctx.decode_token(jwt_token.access_key)
    assert data["name"] == decode_data["name"]


def test_timeout_jwt():
    with pytest.raises(JwtTimeoutError):
        jwt_ctx = JwtContext("test", "HS256", expire=0)
        data = {"name": "kyb"}
        jwt_token = jwt_ctx.create_access_token(data)
        jwt_ctx.decode_token(jwt_token.access_key)
