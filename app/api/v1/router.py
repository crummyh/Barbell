from fastapi import APIRouter

from app.api.v1 import admin, categories, download, images, management, stats, upload

router = APIRouter()

router.include_router(admin.router)
router.include_router(categories.router)
router.include_router(download.router)
router.include_router(images.router)
router.include_router(management.router)
router.include_router(stats.router)
router.include_router(upload.router)
