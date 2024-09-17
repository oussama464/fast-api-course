from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[schemas.Post])
async def get_posts(
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_active_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_active_user),
):
    post_dict = post.model_dump()
    new_post = models.Post(owner_id=user.id, **post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
async def get_post(
    id: int, db: Session = Depends(get_db), user: schemas.UserOut = Depends(oauth2.get_current_active_user)
):
    requested_post = db.query(models.Post).filter(models.Post.id == id).first()
    if requested_post:
        return requested_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int, db: Session = Depends(get_db), user: schemas.UserOut = Depends(oauth2.get_current_active_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    if post.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"user {user.id} : connot delete the post"
        )
    post_query.delete(synchronize_session=False)
    db.commit()


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    new_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_active_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first()
    if not post_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    if post_to_update.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"user {user.id} : connot update the post"
        )
    new_post_dict = new_post.model_dump(exclude_unset=True)
    post_query.update(new_post_dict, synchronize_session=False)  # type: ignore[arg-type]
    db.commit()
    db.refresh(post_to_update)
    return post_to_update
