"""
Called when a user wants to download a dataset. We gather
images, and bundle them into the requested format along
with requested metadata and labels. We then can point
the user to another URL where they can download the entire
file.
"""

from app.models import DownloadFormat


async def create_download_bundle(
    format: DownloadFormat,

)
