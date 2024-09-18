from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    # model_config = ConfigDict(field={"likes": {"exclude": True}})
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOutBase
    likes: list[UserOutBase] = Field(exclude=True)

    @computed_field(alias="total_vote_count")
    def vote_count(self) -> int:
        return len(self.likes)


class UserOutBase(BaseModel):
    id: int
    email: str


class UserOut(UserOutBase):
    created_at: datetime
    liked_posts: list[Post]


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserOut):
    posts: list[Post] | None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None


class Vote(BaseModel):
    post_id: int
    dir: int = Field(
        ...,
        ge=0,
        le=1,
        description="a vote direction of 1 means we want to add a vote, a direction of 0 means we want to delete a vote",
    )


Post.model_rebuild()
UserOut.model_rebuild()
