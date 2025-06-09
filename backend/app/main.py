from fastapi import FastAPI

from .routers import internal_v1, private_v1, public_v1

app = FastAPI()

app.include_router(
    public_v1.router,
    prefix="/public/v1"
)
app.include_router(
    private_v1.router,
    prefix="private/v1"
)
app.include_router(
    internal_v1.router,
    prefix="internal/v1"
)
