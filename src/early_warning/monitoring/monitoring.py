import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def log_prediction(prediction):

    logging.info(f"Prediction generated: {prediction}")
