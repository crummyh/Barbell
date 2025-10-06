from fastapi import APIRouter

from app.api.v1 import admin, categories, download, images, management, stats, upload

router = APIRouter()

router.include_router(admin.router, prefix="/admin")
router.include_router(categories.router, prefix="/categories")
router.include_router(download.router, prefix="/download")
router.include_router(images.router, prefix="/images")
router.include_router(management.router, prefix="/management")
router.include_router(stats.router, prefix="/stats")
router.include_router(upload.router, prefix="/upload")
