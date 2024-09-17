from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.hash_user_password(user.password)
    user.password = hashed_password
    user_dict = user.model_dump()
    new_user = models.User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: Session = Depends(get_db)):
    requested_user = db.query(models.User).filter(models.User.id == id).first()
    if not requested_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with is : {id} was not found")
    return requested_user
