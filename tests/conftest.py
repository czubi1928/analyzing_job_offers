import logging
import os
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# folder = "tmp"


def close_log_handlers():
    """
    Delete and close all handlers from the root logger.
    """
    root_logger = logging.getLogger()
    handlers = root_logger.handlers[:]

    for handler in handlers:
        handler.close()
        root_logger.removeHandler(handler)


def pytest_sessionstart(session, folder="tmp"):
    """
    Execute before the start of the entire test session.
    Here you can create a temporary folder, initialize some global state.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def pytest_sessionfinish(session, exitstatus, folder="tmp"):
    """
    Execute after the entire test session ends.
    Here you can remove the temporary folder.
    """
    close_log_handlers()

    if os.path.exists(folder):
        shutil.rmtree(folder)
