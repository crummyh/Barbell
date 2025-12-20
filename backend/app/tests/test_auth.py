from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.user import User, UserPublic


def test_register(client: TestClient, test_db: Session) -> None:
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


def test_verify(client: TestClient, test_db: Session) -> None:
    code = test_db.exec(select(User).where(User.username == "testUser")).one().code

    data = {"code": code}
    resp = client.get("/auth/v1/verify", params=data)
    assert resp.status_code == 200

    user = test_db.exec(select(User).where(User.username == "testUser")).one()

    assert user
    assert user.code is None
    assert user.disabled is False


def test_token(client: TestClient, test_db: Session) -> None:
    resp = client.post(
        "/auth/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "testUser", "password": "testPassword"},
    )
    assert resp.status_code == 200

    access_cookie = resp.cookies.get("access_token")

    assert access_cookie
    assert client.cookies.get("access_token")

    user_resp = client.get("/auth/v1/users/me")
    assert resp.status_code == 200

    user_pub = UserPublic.model_validate(user_resp.json())
    assert user_pub.username == "testUser"

    logout_resp = client.get("/auth/v1/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.cookies.get("access_token") is None

    failing_resp = client.get("/auth/v1/users/me")
    assert failing_resp.status_code != 200
