from passlib.context import CryptContext  # type: ignore[import-untyped]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_user_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_passowrd(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
