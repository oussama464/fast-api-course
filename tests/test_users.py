from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TetsingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TetsingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_root():
    response = client.get("/")
    msg = response.json().get("message")
    assert msg == "Hello World"
    assert response.status_code == 200


def test_create_user():
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "pass123"})
    result = schemas.UserOut(**res.json())
    print(result)
    assert res.status_code == 201
