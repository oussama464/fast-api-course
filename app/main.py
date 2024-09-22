from fastapi import FastAPI

# models.Base.metadata.create_all(bind=engine) # commented because we use alembic to create table and for migrations
from fastapi.middleware.cors import CORSMiddleware

# from . import models
# from .database import engine
from .routers import auth, post, user, vote

app = FastAPI(
    title="demo votes api",
    description="learn difficult and on demand skills",
    version="0.0.1",
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
