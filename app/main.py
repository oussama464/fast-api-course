from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import (
    engine,
    get_db,
)

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts", response_model=list[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_dict = post.model_dump()
    new_post = models.Post(**post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db)):

    requested_post = db.query(models.Post).filter(models.Post.id == id).first()
    if requested_post:
        return requested_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first():
        post.delete(synchronize_session=False)
        db.commit()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, new_post: schemas.PostCreate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first()
    if post_to_update:
        new_post_dict = new_post.model_dump(exclude_unset=True)
        post_query.update(new_post_dict, synchronize_session=False)  # type: ignore[arg-type]
        db.commit()
        db.refresh(post_to_update)
        return post_to_update
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_dict = user.model_dump()
    new_user = models.User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
