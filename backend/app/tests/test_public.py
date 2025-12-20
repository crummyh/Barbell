from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.upload_batch import UploadBatchPublic
from app.models.user import User


def test_ping(client: TestClient, test_db: Session) -> None:
    resp = client.get("/api/v1/ping")
    assert resp.status_code == 200


def test_good_upload_check(
    client: TestClient, test_db: Session, user: User, api_key: str
) -> None:
    with open("app/tests/assets/good.tar.gz", "rb") as archive:
        files = {"archive": archive}
        params = {
            "hash": "13badf47059115351280b728699642baad1fa580f4c56dc0d5fcb432e154dcdb"
        }
        headers = {"x-api-auth": user.username + ":" + api_key}
        resp = client.post(
            "/api/v1/upload/test", files=files, params=params, headers=headers
        )
    assert resp.status_code == 200


def test_bad_upload_checks(
    client: TestClient, test_db: Session, user: User, api_key: str
) -> None:
    headers = {"x-api-auth": f"{user.username}:{api_key}"}

    with open("app/tests/assets/good.tar.gz", "rb") as archive:
        files = {"archive": archive}
        params = {
            "hash": "ca9969de79afaa936a6c0310b543ff62b8b602db29d4cb4895708bba3b571b27"
        }
        resp = client.post(
            "/api/v1/upload/test", files=files, params=params, headers=headers
        )

    assert resp.status_code == 400

    with open("app/tests/assets/bad.tar.gz", "rb") as archive:
        files = {"archive": archive}
        params = {
            "hash": "ca9969de79afaa936a6c0310b543ff62b8b602db29d4cb4895708bba3b571b27"
        }
        resp = client.post(
            "/api/v1/upload/test", files=files, params=params, headers=headers
        )

    assert resp.status_code == 400

    with open("app/tests/assets/empty.tar.gz", "rb") as archive:
        files = {"archive": archive}
        params = {
            "hash": "85cea451eec057fa7e734548ca3ba6d779ed5836a3f9de14b8394575ef0d7d8e"
        }
        resp = client.post(
            "/api/v1/upload/test", files=files, params=params, headers=headers
        )

    assert resp.status_code == 400


def test_upload(client: TestClient, test_db: Session, user: User, api_key: str) -> None:
    headers = {"x-api-auth": user.username + ":" + api_key}
    with open("app/tests/assets/good.tar.gz", "rb") as archive:
        files = {"archive": archive}
        params = {
            "hash": "13badf47059115351280b728699642baad1fa580f4c56dc0d5fcb432e154dcdb"
        }
        resp = client.post(
            "/api/v1/upload", files=files, params=params, headers=headers
        )

    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data
    data = UploadBatchPublic.model_validate(json_data)
    assert data
    assert data.error_message is None
    assert data.username == user.username
