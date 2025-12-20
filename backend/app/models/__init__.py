"""
Models package - import individual models as needed.
"""


def configure_relationships() -> None:
    """Call this after importing models to resolve relationships"""
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
