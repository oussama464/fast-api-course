from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/login", tags=["authentication"])


@router.post("/", response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. retrieve user from db , if user does not exist raise httpexception
    # 2. hash the password and compare to the hash from the database,if not equal raise httpexception
    # 3. create the token and return it as payload

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invaild credentials")
    if not utils.verify_passowrd(user_credentials.password, user.password):  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    access_token = oauth2.create_acess_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


# Important Fields in OAuth2PasswordRequestForm:

#     username: The user’s username (from the form).
#     password: The user’s password (from the form).
#     scope: Optional, but you can define different access levels (e.g., read, write).
#     client_id and client_secret: Optional fields, primarily used in more complex OAuth2 setups where client credentials are needed.
