"""
This file serves as an interop between the main app and AWS S3.
Because I haven't set S3 up yet, it also allows me to test with
a filesystem instead!
"""

from typing import BinaryIO


def create_s3_bucket(name: str):
    pass

def upload_file(file: BinaryIO, bucket: str, object_name: str):
    pass

def download_file(object_name: str, file_name: str):
    pass
