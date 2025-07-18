"""
Called when a user wants to download a dataset. We gather
images, and bundle them into the requested format along
with requested metadata and labels. We then can point
the user to another URL where they can download the entire
file.
"""

from uuid import UUID


async def create_download_batch(batch_id: UUID):
    pass
