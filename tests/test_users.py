from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app import schemas
from app.config import settings
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TetsingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def override_get_db():
    db = TetsingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
