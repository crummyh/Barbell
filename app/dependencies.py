import hashlib

from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

api_key_scheme = APIKeyHeader(name="x-api-key")
limiter = Limiter(key_func=get_remote_address)

def hash_key(api_key: str):
    return hashlib.sha256(api_key.encode()).hexdigest()

def check_api_key(api_key: str):
    hash = hash_key(api_key)
    # same = (hash == #Get hash from database)
