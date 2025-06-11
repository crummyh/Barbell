from fastapi.security import APIKeyQuery
from slowapi import Limiter
from slowapi.util import get_remote_address

api_key_scheme = APIKeyQuery(name="api_key")
limiter = Limiter(key_func=get_remote_address)
