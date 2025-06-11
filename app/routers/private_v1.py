from fastapi import APIRouter, Response
from fastapi.security import APIKeyQuery

from ..dependencies import limiter

router = APIRouter()

@router.get("/status/{batch_id}")
@limiter.limit("10/second")
def get_batch_status(response: Response, batch_id: int, api_key: APIKeyQuery):
    pass

@router.post("/upload")
@limiter.limit("5/minutes")
def upload(responce: Response):
    pass

@router.get("/download")
def download_batch(responce: Response):
    pass

@router.get("/download/{image_id}")
def download_image(responce: Response, image_id: int):
    pass
