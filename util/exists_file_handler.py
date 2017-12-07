import os
import logging


class ExistsFileHandler(logging.FileHandler):
    """
    Custom implementation of a logging file handler which makes sure the directories up to
    the desired log file exist.
    The logfile itself will be automatically created if it doesn't exist yet.
    """
    def __init__(self, filename, mode='a', encoding=None, delay=0):
        # Make sure the directories up to the filename exist!
        log_folder = os.path.dirname(filename)
        os.makedirs(log_folder, exist_ok=True)

        super().__init__(filename, mode, encoding, delay)
