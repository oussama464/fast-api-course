from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote, db: Session = Depends(get_db), user: schemas.UserOut = Depends(oauth2.get_current_active_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    post_to_vote_on = post_query.first()
    if not post_to_vote_on:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id : {vote.post_id} was not found"
        )
    vote_query = db.query(models.likes_table).filter(
        models.likes_table.c.post_id == vote.post_id, models.likes_table.c.user_id == user.id
    )  # type: ignore[attr-defined]
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user: {user.id} has already voted on post: {vote.post_id} ",
            )

        new_vote = models.likes_table.insert().values(user_id=user.id, post_id=vote.post_id)
        db.execute(new_vote)
        db.commit()

        return {"message": "successfully added vote"}

    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote does not exits")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully deleted vote"}
