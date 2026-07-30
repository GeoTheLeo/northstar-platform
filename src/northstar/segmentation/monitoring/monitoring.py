"""
Segmentation monitoring utilities.
"""

from northstar.logging import logger


def log_segmentation(message: str) -> None:
    """
    Log segmentation events.
    """

    logger.info(message)