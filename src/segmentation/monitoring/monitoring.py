import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def log_segmentation(message):

    logging.info(message)