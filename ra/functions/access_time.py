import time
import logging
logger = logging.getLogger('django')


def measure(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        res = func.__name__ + " " + str(end-start)
        logger.info(res)
        return result
    return wrapper