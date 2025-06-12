from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

api_key_scheme = APIKeyHeader(name="x-api-key")
limiter = Limiter(key_func=get_remote_address)
