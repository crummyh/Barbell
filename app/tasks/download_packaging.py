"""
Called when a user wants to download a dataset. We gather
images, and bundle them together along with requested
metadata and labels. We then can point the user to another
URL where they can download the entire file.
"""

import hashlib
import json
import random
import tarfile
from datetime import datetime, timezone
from io import BytesIO, TextIOWrapper
from uuid import UUID

from sqlmodel import Session, func, select

from app.core import config
from app.core.helpers import UUIDEncoder
from app.database import engine
from app.models.models import DownloadStatus
from app.models.schemas import DownloadBatch, Image, LabelCategory, LabelSuperCategory
from app.services.buckets import (
    get_image,
    update_download_batch,
)

# Define a base template for manifests
BASE_COCO_MANIFEST = {
    "info": {
        "description": "Barbell Open Dataset",
        "url": config.PROJECT_URL,
        "version": config.PROJECT_VERSION,
        "year": str(datetime.now(timezone.utc).year),
        "contributor": "",
        "date_created": str(datetime.now(timezone.utc).date)
    },
    "licenses": [
        {"url": "https://creativecommons.org/licenses/by-nc/4.0/","id": 0,"name": "Creative Commons Attribution-NonCommercial 4.0 International"}
    ],
    "images": [],
    "annotations": [],
    "categories": []
}

def create_download_batch(batch_id: UUID):
    with Session(engine) as session:
        batch = session.get(DownloadBatch, batch_id) # Get the batch

        if not batch:
            raise ValueError(f"DownloadBatch with id {batch_id} not found")

        try:
            batch.status = DownloadStatus.ASSEMBLING_LABELS
            session.add(batch)
            session.commit()

            manifest = BASE_COCO_MANIFEST.copy() # Make a copy of the manifest
            annotation_category_id_list = [] # Store the selected ids so I don't have to loop later

            for selection in batch.annotations:
                try:
                    if selection.super:
                        # If the selection is super, include all children
                        super_cat = session.get(LabelSuperCategory, selection.id)
                        for category in super_cat.sub_categories:
                            manifest["categories"].append({
                                "supercategory": super_cat.name,
                                "id": category.id,
                                "name": category.name
                            })
                            annotation_category_id_list.append(category.id)
                    else:
                        # The selection is not super, add it alone
                        category = session.get(LabelCategory, selection.id)

                        if category.super_category:
                            manifest["categories"].append({
                                "supercategory": category.super_category.name,
                                "id": category.id,
                                "name": category.name
                            })
                        else:
                            manifest["categories"].append({
                                "id": category.id,
                                "name": category.name
                            })
                        annotation_category_id_list.append(category.id)

                except Exception:
                    pass

            batch.status = DownloadStatus.ASSEMBLING_IMAGES
            session.add(batch)
            session.commit()

            archive_obj = BytesIO()
            with tarfile.open(fileobj=archive_obj, mode="w:gz") as archive:
                images = _get_random_images(session, batch.image_count)
                for image in images:
                    manifest["images"].append({
                        "id": image.id,
                        "license": 0,
                        "width": 640,
                        "hight": 640,
                        "file_name": str(image.id) + "." + config.IMAGE_STORAGE_FORMAT,
                        "date_captured": image.created_at.strftime("%y-%m-%d %H:%M:%S")
                    })

                    image_obj = get_image(image.id)
                    image_obj.seek(0,2)
                    size = image_obj.tell()
                    image_obj.seek(0)

                    tar_info = tarfile.TarInfo(name=str(image.id) + "." + config.IMAGE_STORAGE_FORMAT)
                    tar_info.size = size
                    tar_info.mtime = image.created_at.timestamp()
                    tar_info.mode = 0o644

                    archive.addfile(tarinfo=tar_info, fileobj=image_obj)

                    for annotation in image.annotations:
                        if annotation.category_id in annotation_category_id_list:
                            manifest["annotations"].append({
                                "id": annotation.id,
                                "category_id": annotation.category_id,
                                "iscrowd": annotation.iscrowd,
                                "area": annotation.bbox_h * annotation.bbox_w,
                                "bbox": [
                                    annotation.bbox_x,
                                    annotation.bbox_y,
                                    annotation.bbox_w,
                                    annotation.bbox_h
                                ]
                            })

                batch.status = DownloadStatus.ADDING_MANIFEST
                session.add(batch)
                session.commit()

                manifest_obj = BytesIO()
                with TextIOWrapper(manifest_obj, encoding="utf-8", write_through=True) as wrapper:
                    json.dump(manifest, wrapper, cls=UUIDEncoder)

                manifest_obj.seek(0)

                tar_info = tarfile.TarInfo(name="manifest.json")

                manifest_obj.seek(0, 2)  # Move to end to get size
                tar_info.size = manifest_obj.tell()
                manifest_obj.seek(0)     # Rewind for reading

                tar_info.mtime = datetime.now(timezone.utc).timestamp()
                tar_info.mode = 0o644

                archive.addfile(tarinfo=tar_info, fileobj=manifest_obj)

            archive_obj.seek(0)
            update_download_batch(batch_id, archive_obj)

            archive_obj.seek(0)
            batch.hash = hashlib.sha256(archive_obj.read()).hexdigest()

            batch.status = DownloadStatus.READY
            session.add(batch)
            session.commit()

        except Exception as e:
            session.rollback()
            batch.status = DownloadStatus.FAILED
            batch.error_message = str(e)
            session.add(batch)
            session.commit()
            raise

def _get_random_images(session: Session, count: int):
    # First, get the total count
    total_images = session.exec(select(func.count()).select_from(Image)).one()

    if total_images == 0:
        return []

    # Calculate a random offset, making sure we don't go out of bounds
    max_offset = max(0, total_images - count)
    offset = random.randint(0, max_offset)

    # Fetch `count` images starting from the offset
    images = session.exec(
        select(Image)
        .offset(offset)
        .limit(count)
    )

    return images
