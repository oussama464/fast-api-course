from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint, text
from sqlalchemy.orm import backref, relationship

from .database import Base

# association table establishes many to many relationships between posts and likes
# one post can be liked by many users
# one user can like many posts
# the many to many relationship is not between user and posts in terms of ownership
# instead it it is between user and posts in term of likes/votes
likes_table = Table(
    "votes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "post_id", name="user_post_unique"),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # many to one relationship to users
    owner = relationship("User", back_populates="posts")
    # association table
    likes = relationship("User", secondary=likes_table, back_populates="liked_posts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # one to many relationship to posts
    posts = relationship("Post", back_populates="owner")
    # association table
    liked_posts = relationship("Post", secondary=likes_table, back_populates="likes")
