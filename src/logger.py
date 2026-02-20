""" Code to set up Logging
    Provides Logging Utitlites that make Multiprocessing Logging
"""

import logging
import time
from logging import StreamHandler, FileHandler
from logutils.queue import QueueHandler, QueueListener

def initialize_logging(level, queue):
    """Setup logging for a process.

    Creates a base logger for deFNd.  Installs a single handler, which will
    send packets across a queue to the logger process.  This function should be
    called by each of the three worker processes before they start.

    """
    formatter = _get_formatter()

    logger = logging.getLogger('pywall')
    if not logger.handlers:  # Check if handler already exists
        logger.setLevel(level)

        handler = QueueHandler(queue)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

def _get_formatter():
    #creates a formatter with a specified format for log message
    return logging.Formatter(fmt='[%(asctime)s][%(levelname)s] %(message)s')

def log_server(level, queue, filename=None, mode='w'):
    """Run the logging server.

    This listens to the queue of log messages, and handles them using Python's
    logging handlers. It prints to stderr, as well as to a specified file, if
    it is given.

    """
    formatter = _get_formatter()

    handlers = [StreamHandler()]
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)

    if filename:
        file_handler = FileHandler(filename, mode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        handlers.append(file_handler)

    listener = QueueListener(queue, *handlers)
    listener.start()

    try:
        listener.join()  # Wait for the listener to terminate
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
