from fastapi.testclient import TestClient

from app import schemas
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    msg = response.json().get("message")
    assert msg == "Hello World"
    assert response.status_code == 200


def test_create_user():
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "pass123"})
    # result = schemas.UserOut(**res.json())
    # print(result)
    assert res.status_code == 201
