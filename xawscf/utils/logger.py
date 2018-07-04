import logging

logger = logging.getLogger(__name__.split('.')[0])
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
logger.addHandler(handler)

def log(message):
    logger.info(message)

def logError(err):
    logger.error(err)
