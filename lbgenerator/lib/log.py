
from .. import config
import logging

class Logger():

    """ The logger class
    """
    def __init__(self, module):
        """ Get configurations and build the logger object
        """
        """
        # Build logging object
        self.logger = logging.getLogger(module)
        self.logger.setLevel(logging.INFO)

        # Configure log format
        formatter = logging.Formatter(config.LOG_FORMAT)

        # Set log file
        handler = logging.FileHandler(config.LOG_FILE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        #self.enabled = config.LOG_ENABLED
        self.enabled = True
        """

    def log(self, msg):
        pass

    def __getattr__(self, name):
        # debug, info, error, warn
        level = getattr(logging, name.upper())
        self.logger.setLevel(level)
        if self.enabled:
            return getattr(self.logger, name)
        else:
            return self.log


