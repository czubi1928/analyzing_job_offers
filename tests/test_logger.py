import os

import pytest

from app.logger import Logger


@pytest.fixture
def test_logger():
    """
    Fixture that creates a logger with a temporary log file.
    """
    return Logger(log_folder="tmp")


def test_logger_file_created(test_logger):
    """
    Checks whether a log file is created after logging in.
    """
    test_logger.info("Test log message.")
    log_path = test_logger.logger.handlers[0].baseFilename  # takes the path to the file

    assert os.path.exists(test_logger.logs_folder), "Logs folder does not exist!"
    assert os.path.isfile(log_path), "The log file was not created!"


def test_logger_info_level(test_logger, caplog, test_variable="INFO test message."):
    """
    It verifies that logging at the INFO level works.
    In this test, we also verify the output to the console (capsys).
    """
    test_logger.info(test_variable)

    assert test_variable in caplog.text


def test_logger_debug_level(test_logger, caplog, test_variable="DEBUG test message."):
    """
    Verifies that DEBUG level logging works and that it appears on the console.
    """
    test_logger.debug(test_variable)

    assert test_variable in caplog.text


def test_logger_warning_level(test_logger, caplog, test_variable="Warning!"):
    """
    Verifies that WARNING level logging is working.
    """
    test_logger.warning(test_variable)

    assert test_variable in caplog.text
