import logging
import os
class  Logger:
    instance = None
    def __init__(self):
        # Get a logger instance
        self.instance = logging.getLogger(__name__)
        self.instance.setLevel(logging.DEBUG)
        LOGS_DIR = "logs"
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        # Set up a file handler that changes every day
        from datetime import date
        today = date.today()
        log_file = f"log_{today.strftime('%Y-%m-%d')}.txt"
        file_handler = logging.FileHandler(LOGS_DIR + "/" + log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # Set up a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.instance.addHandler(file_handler)
        self.instance.addHandler(console_handler)
    def get_logger(self):
        return self.instance
    def debug(self, message):
        self.instance.debug(message)
    def info(self, message):
        self.instance.info(message)
    def warning(self, message):
        self.instance.warning(message)
    def error(self, message, exc_info=True):
        self.instance.error(message, exc_info=exc_info)
    def critical(self, message):
        self.instance.critical(message)
