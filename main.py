from random import randrange

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


my_posts = [
    {"title": "top beaches in florida", "content": "check out these awesome beaches", "rating": 11, "id": 1},
    {"title": "favourite food", "content": "I Like pizza!", "id": 2},
]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts")
async def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 100000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    for post in my_posts:
        if id == post["id"]:
            return {"post_detail": post}
    # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"message": f"post with id {id} was not found"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    for index, post in enumerate(my_posts):
        if id == post["id"]:
            my_posts.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")


@app.put("/posts/{id}")
def update_post(id: int, new_post: Post):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            new_post_dict = new_post.model_dump()
            new_post_dict["id"] = id
            print(index)
            my_posts[index] = new_post_dict
        return {"detail": new_post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
