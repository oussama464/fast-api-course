from datetime import datetime, timedelta, timezone
from turtle import settiltangle

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, PyJWTError
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .database import get_db

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_acess_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def verify_access_token(credentials_exception: HTTPException, token: str):

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         id: str = payload.get("user_id")
#         if id is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(id=id)
#     except PyJWTError as e:
#         raise credentials_exception from e
#     else:
#         return token_data


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return verify_access_token(credentials_exception, token)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)  # type: ignore[arg-type]
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = db.query(models.User).filter(models.User.id == token_data.id).first()

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.UserOut = Depends(get_current_user),
):
    return current_user
