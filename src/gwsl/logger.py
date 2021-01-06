import logging


def init_logger(out_path):
    logger = logging.getLogger(__name__)
    # Create handlers
    f_handler = logging.FileHandler(out_path)
    f_handler.setLevel(logging.ERROR)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    # Add handlers to the logger
    logger.addHandler(f_handler)
    return logger
