import uvicorn
from fastapi import FastAPI

from .routers import api_v1, web

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
        "description": "Acessing these endpoints does not require an API key",
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
    openapi_tags=tags_metadata
)

app.include_router(api_v1.router, prefix="/api/v1")
app.include_router(web.router, include_in_schema=False)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
