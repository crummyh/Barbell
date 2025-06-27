"""
Called when a user wants to download a dataset. We gather
images, and bundle them into the requested format along
with requested metadata and labels. We then can point
the user to another URL where they can download the entire
file.
"""

from app.models import DownloadRequest


async def create_download_bundle(request: DownloadRequest):
    pass
