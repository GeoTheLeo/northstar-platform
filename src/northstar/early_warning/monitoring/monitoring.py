"""
Early Warning monitoring utilities.
"""

from northstar.logging import logger


def log_prediction(prediction: int) -> None:
    """
    Log an Early Warning prediction.
    """

    logger.info(
        "Prediction generated: %s",
        prediction,
    )