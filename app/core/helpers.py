import hashlib
import json
from typing import BinaryIO
from uuid import UUID

from app.core import config


def get_hash_with_streaming(file: BinaryIO, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    file.seek(0)
    while True:
        data = file.read(config.HASHING_BUF_SIZE)
        if not data:
            break
        h.update(data)

    return h.hexdigest()


class UUIDEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            # if the o is uuid, we return the value of uuid
            return o.hex
        return json.JSONEncoder.default(self, o)
