import logging
import os
from logging.handlers import RotatingFileHandler


def _get_formatter():
    """
    Helper method to create a log formatter.

    :returns: The format in which the logs are to be saved.
    """
    return logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )


class Logger:
    def __init__(
            self,
            log_folder="logs",
            log_filename="app.log",
            log_to_file=True,
            log_to_console=True,
            max_log_size=128 * 1024 * 1024,  # 128 MB
            backup_count=7,
            project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            # logger_name="job_offers_app",
    ):
        # self.logger = logging.getLogger(logger_name)
        self.logger = logging.getLogger()

        self.logger.handlers.clear()

        self.logs_folder = os.path.join(project_root, log_folder)

        # Ensure no duplicate handlers
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.DEBUG)

            if log_to_file:
                # Ensure the log folder exists
                if not os.path.exists(self.logs_folder):
                    os.makedirs(self.logs_folder)

                # Full path to the log file
                log_file_path = os.path.join(self.logs_folder, log_filename)

                # File handler with rotation
                file_handler = RotatingFileHandler(
                    log_file_path, maxBytes=max_log_size, backupCount=backup_count
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(_get_formatter())
                self.logger.addHandler(file_handler)

            # Console handler
            if log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(_get_formatter())
                self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
