from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.models import User


def test_register(client: TestClient, test_db: Session):
    data = {
        "username": "testUser",
        "email": "test@example.com",
        "password": "testPassword",
    }
    resp = client.post("/auth/v1/register", json=data)
    assert resp.status_code == 200

    db_user = test_db.exec(select(User).where(User.username == "testUser")).one()

    assert db_user
    assert db_user.username == "testUser"
    assert db_user.email == "test@example.com"
    assert db_user.disabled is True
    assert db_user.code

def test_verify(client: TestClient, test_db: Session):
    code = test_db.exec(select(User).where(User.username == "testUser")).one().code

    data = {"code": code}
    resp = client.get("/auth/v1/verify", params=data)
    assert resp.status_code == 200

    user = test_db.exec(select(User).where(User.username == "testUser")).one()

    assert user
    assert user.code is None
    assert user.disabled is False

def test_token(client: TestClient, test_db: Session):

    resp = client.post(
        "/auth/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "testUser", "password": "testPassword"}
    )
    assert resp.status_code == 200

    access_cookie = resp.cookies.get("access_token")

    assert access_cookie
