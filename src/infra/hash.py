from passlib.context import CryptContext

ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(plain: str) -> str:
    return ctx.hash(plain)


def verify_hash(plain, hashed) -> bool:
    return ctx.verify(plain, hashed)
