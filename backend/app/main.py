from fastapi import FastAPI

from .routers import private_v1, public_v1

app = FastAPI()

app.include_router(
    public_v1.router,
    prefix="/public/v1"
)
app.include_router(
    private_v1.router,
    prefix="private/v1"
)