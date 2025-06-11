from fastapi import FastAPI

from .routers import api_v1, web

app = FastAPI()

app.include_router(
    api_v1.router,
    prefix="/api/v1"
)
app.include_router(web.router)
