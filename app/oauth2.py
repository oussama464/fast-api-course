from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "0ec4b4c488b6b470cdbb326b7f651b8a43caf2c9b11eced50c2f7c1a3e5c85b2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_acess_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
