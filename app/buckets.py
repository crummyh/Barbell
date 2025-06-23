"""
This file serves as an interop between the main app and AWS S3.
Because I haven't set S3 up yet, it also allows me to test with
a filesystem instead!
"""

from typing import BinaryIO

from pydantic.types import UUID4

from app import config
from app.helpers import get_hash_with_streaming

_init = False

def init():
    try:
        _create_s3_bucket(config.IMAGES_BUCKET_NAME)
        _create_s3_bucket(config.UPLOAD_BATCHES_BUCKET_NAME)
        _init = True
    except:  # noqa: E722
        raise Exception()

def create_upload_batch(archive: BinaryIO, uuid: UUID4):
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(archive, config.UPLOAD_BATCHES_BUCKET_NAME, str(uuid))

def create_image(image: BinaryIO, uuid: UUID4):
    """ NOTE: IMAGE MUST BE OPENED WITH `'rb'` """
    if not _init:
        raise Exception("Buckets where not initialized. Run `init()`")

    _upload_file(image, config.IMAGES_BUCKET_NAME, str(uuid))

def _create_s3_bucket(name: str):
    pass

def _upload_file(file: BinaryIO, bucket: str, object_name: str):
    pass

def _download_file(object_name: str, file_name: str):
    pass
