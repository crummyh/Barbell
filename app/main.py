from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api import auth_v1, internal_v1, public_v1, web
from app.db.database import init_db
from app.services import buckets
from app.services.monitoring import start_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    buckets.init()
    start_monitor()
    yield

description = """
Docs and stuff goes here!!!
"""

tags_metadata = [
    {
        "name": "Stats",
        "description": "Get *information* about the dataset",
    },
    {
        "name": "Public",
        "description": "Accessing these endpoints does not require an API key",
    },
    {
        "name": "Auth Required",
        "description": "An API key is needed to access these endpoints"
    }
]

app = FastAPI(
    title="Open FRC Vision",
    description=description,
    summary="Upload and download training data for FRC object detection.",
    version="0.0.1",
    terms_of_service="terms here",
    contact={
        "name": "Elijah Crum",
        "email": "elijah@crums.us"
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/crummyh/frcVisonDataset/blob/main/LICENSE"
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None
)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.mount("/internal", internal_v1.subapp) # TODO: Disable docs
app.include_router(public_v1.router, prefix="/api/v1")
app.include_router(web.router, include_in_schema=False)
app.include_router(auth_v1.router)

@app.get("/docs/api", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        swagger_favicon_url="/static/images/favicon.ico",
    )

@app.get("/docs/api/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        redoc_favicon_url="/static/images/favicon.ico",
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
