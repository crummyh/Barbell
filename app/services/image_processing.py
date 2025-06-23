from pathlib import Path

from pydantic.types import UUID4
from sqlmodel import Session


async def process_batch_async(batch_id: UUID4, session: Session):
    pass

def validate_image(image_path: Path) -> bool:
    """Validate image meets requirements (640x640, etc.)"""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size == (640, 640)
    except:
        return False
