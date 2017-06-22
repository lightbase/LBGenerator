import logging
from .. import config


class Logger():

    """ The logger class
    """
    def __init__(self, module):
        """ Get configurations and build the logger object
        """

    def log(self, msg):
        pass

    def __getattr__(self, name):

        # NOTE: "debug", "info", "error" and "warn"! By John Doe
        level = getattr(logging, name.upper())
        self.logger.setLevel(level)
        if self.enabled:
            return getattr(self.logger, name)
        else:
            return self.log
