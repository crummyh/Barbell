from fastapi import APIRouter

router = APIRouter()

@router.get("/status/{batch_id}")
def get_batch_status(batch_id: int):
    pass

@router.post("/upload")
def upload():
    pass

@router.get("/download")
def download_batch():
    pass

@router.get("/download/{image_id}")
def download_image(image_id: int):
    pass
