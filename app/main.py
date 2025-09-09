from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth_v1, internal_v1, public_v1, web
from app.core import config
from app.database import init_db
from app.services import buckets
from app.services.monitoring import start_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    buckets.init()
    start_monitor()
    web.load_snippets()
    yield

description = """
I need to put docs and stuff here
"""

tags_metadata = [
    {
        "name": "Download",
        "description": "Download full training sets",
        "externalDocs": {
            "description": "Download docs",
            "url": config.URL_PREFIX + config.PROJECT_URL + "/docs/upload"
        }
    },
    {
        "name": "Upload",
        "description": "Upload match images",
        "externalDocs": {
            "description": "Upload docs",
            "url": config.URL_PREFIX + config.PROJECT_URL + "/docs/download"
        }
    },
    {
        "name": "Stats",
        "description": "Get stats about the database"
    },
    {
        "name": "Management",
        "description": "Manage your account",
    },
    {
        "name": "Auth",
        "description": "Advanced Authentication",
        "externalDocs": {
            "description": "Auth docs",
            "url": config.URL_PREFIX + config.PROJECT_URL + "/docs/auth"
        }
    }
]

app = FastAPI(
    title="Barbell",
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
        "url": "https://github.com/crummyh/Barbell/blob/main/LICENSE"
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None
)

app.debug = config.DEBUG

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.mount("/internal", internal_v1.subapp) # TODO: Disable docs
app.include_router(public_v1.router, prefix="/api/v1")
app.include_router(web.router, include_in_schema=False)
app.include_router(auth_v1.router, prefix="/auth/v1")

def not_found_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"},
    )

@app.exception_handler(404)
def not_found_exception_handler(
    request: Request,
    exc: HTTPException,
):
    path = str(request.url).replace(str(request.base_url),"")
    if "api" in path or "auth" in path or "internal" in path or "static" in path:
        return not_found_error(request, exc)
    else:
        return web.not_found_page(request=request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
