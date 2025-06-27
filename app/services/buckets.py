"""
This file serves as an interop between the main app and AWS S3.
Because I haven't set S3 up yet, it also allows me to test with
a filesystem instead!
"""

from typing import IO

from pydantic.types import UUID4

from app.core import config

_init = False

def init():
    try:
        _create_s3_bucket(config.IMAGES_BUCKET_NAME)
        _create_s3_bucket(config.UPLOAD_BATCHES_BUCKET_NAME)
        _init = True
    except Exception:
        raise

def create_upload_batch(archive: IO[bytes], uuid: UUID4):
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(archive, config.UPLOAD_BATCHES_BUCKET_NAME, str(uuid))

def get_upload_batch(uuid: UUID4) -> IO[bytes]:
    return _download_file(uuid.hex, uuid.hex)

def create_image(image: IO[bytes], uuid: UUID4):
    """ NOTE: IMAGE MUST BE OPENED WITH `'rb'` """
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(image, config.IMAGES_BUCKET_NAME, str(uuid))

def _create_s3_bucket(name: str):
    pass

def _upload_file(file: IO[bytes], bucket: str, object_name: str):
    pass

def _download_file(object_name: str, file_name: str) -> IO[bytes]:
    return IO[bytes]()
