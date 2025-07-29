import logging
import os

def setup_logger(log_file='logs/app_errors.log'):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(message)s'
    )

def log_error(error_msg, exc_info=True):
    logging.error(error_msg, exc_info=exc_info)
