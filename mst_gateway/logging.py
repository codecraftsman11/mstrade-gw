import logging
import sys


DEFAULT_LOG_FORMAT = '[%(asctime)s] %(threadName)-10s %(levelname)-8s %(message)s'
DEFAULT_LOG_LEVEL = logging.ERROR
DEFAULT_LOG_STREAM = sys.stdout


def init_logger(name='root', **kwargs):
    if name == 'root':
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)
    logger.setLevel(kwargs.get('level', DEFAULT_LOG_LEVEL))

    if kwargs.get('filename'):
        handler = logging.FileHandler(
            filename=kwargs.get('filename'),
            mode=kwargs.get('mode', 'a'),
            encoding=kwargs.get('encoding', None),
            delay=kwargs.get('delay', False))
    else:
        handler = logging.StreamHandler(kwargs.get('stream', DEFAULT_LOG_STREAM))

    formatter = logging.Formatter(kwargs.get('format', DEFAULT_LOG_FORMAT))

    handler.setLevel(kwargs.get('level', DEFAULT_LOG_LEVEL))
    handler.setFormatter(formatter)

    for hnd in logger.handlers:
        logger.removeHandler(hnd)
    logger.addHandler(handler)

    return logger


def create_logger(name='root', loglevel='INFO', logfile=None, **kwargs):
    level = getattr(logging, loglevel.upper(), logging.INFO)
    if logfile is None or logfile.lower() == "stdout":
        return init_logger(name=name, level=level, **kwargs)
    return init_logger(name=name, level=level, filename=logfile, **kwargs)
