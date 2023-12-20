import inspect
import logging
import os
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath

logger = logging.getLogger(__name__)


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    dark_grey = "\x1b[38;5;247m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt=None):
        super().__init__()
        # Define format for logs
        if fmt:
            self.fmt = fmt
        else:
            self.fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
        self.FORMATS = {
            logging.DEBUG: self.dark_grey + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logger(
    loglevel: str, format="%(asctime)s | %(levelname)-8s | %(message)s"
):
    # The log file name will be the name of the caller module (caller_module_name.log)
    # in the <log_dir_name> folder
    log_dir_name = Path("logs")
    log_dir_name.mkdir(parents=True, exist_ok=True)
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    log_filename = PurePath(module.__file__).with_suffix(".log").name
    if os.name == "posix":
        log_file_path = PurePosixPath(log_dir_name).joinpath(log_filename)
    else:
        log_file_path = PureWindowsPath(log_dir_name).joinpath(log_filename)
    logging.basicConfig(
        filename=f"{log_file_path}", filemode="a", format=format, level=loglevel.upper()
    )

    logger.setLevel(level="DEBUG")
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(level=loglevel.upper())
    stdout_handler.setFormatter(CustomFormatter(fmt=format))
    logger.addHandler(stdout_handler)

    logger.debug(f"Log file path: {log_file_path}")
