import logging
import os
from datetime import datetime

class Logger:
    LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    @classmethod
    def setup_logger(cls, log_callback=None):
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(cls.LOG_FILE, encoding="utf-8", mode='a')
            ]
        )

        if log_callback:
            cls.ui_handler = UILogHandler(log_callback)
            cls.ui_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', '%H:%M:%S'))
            logging.getLogger().addHandler(cls.ui_handler)


    @classmethod
    def log_info(cls, message: str):
        logging.info(message)

    @classmethod
    def log_warning(cls, message: str):
        logging.warning(message)

    @classmethod
    def log_error(cls, message: str):
        logging.error(message)



from logging import Handler

class UILogHandler(Handler):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback

    def emit(self, record):
        log_entry = self.format(record)
        if self.log_callback:
            self.log_callback(log_entry)
