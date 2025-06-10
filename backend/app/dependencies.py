from fastapi.security import APIKeyQuery

api_key_scheme = APIKeyQuery(name="api_key")
