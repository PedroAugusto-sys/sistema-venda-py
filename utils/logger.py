import logging
import os

_configured = False

def get_logger(name="app"):
    global _configured
    logger = logging.getLogger(name)
    if _configured:
        return logger

    os.makedirs("logs", exist_ok=True)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _configured = True
    return logger
