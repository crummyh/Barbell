"""
This file serves as an interop between the main app and AWS S3.
Because I haven't set S3 up yet, it also allows me to test with
a filesystem instead!
"""

import os
from typing import BinaryIO
from uuid import UUID

from app.core import config

_init = False
# _DATA_PATH = "../data"
_DATA_PATH = "data"  # Needs to change for real testing


def init():
    global _init
    try:
        if not os.path.exists(_DATA_PATH):
            os.makedirs(_DATA_PATH)

        _create_s3_bucket(config.IMAGES_BUCKET_NAME)
        _create_s3_bucket(config.UPLOAD_BATCHES_BUCKET_NAME)
        _create_s3_bucket(config.DOWNLOAD_BATCHES_BUCKET_NAME)
        _init = True

    except Exception:
        raise


def create_upload_batch(archive: BinaryIO, uuid: UUID):
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(archive, config.UPLOAD_BATCHES_BUCKET_NAME, str(uuid))


def get_upload_batch(uuid: UUID) -> BinaryIO:
    return _download_file(str(uuid), config.UPLOAD_BATCHES_BUCKET_NAME)


def update_download_batch(uuid: UUID, new_archive: BinaryIO):
    _upload_file(
        new_archive, config.DOWNLOAD_BATCHES_BUCKET_NAME, str(uuid) + ".tar.gz"
    )


def get_download_batch(uuid: UUID) -> BinaryIO:
    """
    Eventually, this needs to stream. It should look like this:
        obj = s3.get_object(Bucket="my-bucket", Key=key)
        body = obj["Body"]  # This is a streaming response from boto3

        return StreamingResponse(
            body,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={key}"}
        )
    """
    return _download_file(str(uuid) + ".tar.gz", config.UPLOAD_BATCHES_BUCKET_NAME)


def create_image(image: BinaryIO, uuid: UUID):
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(image, config.IMAGES_BUCKET_NAME, str(uuid))


def get_image(uuid: UUID) -> BinaryIO:
    return _download_file(str(uuid), config.IMAGES_BUCKET_NAME)


def _create_s3_bucket(name: str):
    if not os.path.exists(_DATA_PATH + "/" + name):
        os.makedirs(_DATA_PATH + "/" + name)


def _upload_file(file: BinaryIO, bucket: str, object_name: str):
    with open(_DATA_PATH + "/" + bucket + "/" + object_name, "wb") as f:
        file.seek(0)
        f.write(file.read())


def _download_file(object_name: str, bucket: str) -> BinaryIO:
    return open(_DATA_PATH + "/" + bucket + "/" + object_name, "rb")
