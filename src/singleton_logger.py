"""
singleton logger to use everywhere (don't use prints to log!!)
"""
import logging
import os
import datetime

class SingletonType(type):
    """
    Metaclass for implementing the Singleton design pattern.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override the __call__ method to ensure only one instance of the class is created.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(object, metaclass=SingletonType):
    """
    Singleton Logger class for logging messages.
    """
    _logger = None

    def __init__(self):
        """
        Initialize the Logger instance.
        """
        self._logger = logging.getLogger("crumbs")
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s \t [%(levelname)s | %(filename)s:%(lineno)s] > %(message)s')

        now = datetime.datetime.now()
        dirname = "./log"

        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        fileHandler = logging.FileHandler(dirname + "/log_" + now.strftime("%Y-%m-%d_%H-%M") + ".log", encoding='utf-8')

        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)

        self._logger.addHandler(fileHandler)
        self._logger.addHandler(streamHandler)

        print("Generate new instance")

    def get_logger(self):
        """
        Get the logger instance.
        Returns:
            logging.Logger: The logger instance.
        """
        return self._logger