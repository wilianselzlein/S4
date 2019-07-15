import traceback
import functools
from flask import jsonify
import logging
from colorlog import ColoredFormatter
import config
import coloredlogs

def get_logger(name):
    # logger.debug("this is a debugging message")
    # logger.info("this is an informational message")
    # logger.warning("this is a warning message")
    # logger.error("this is an error message")
    # logger.critical("this is a critical message")

    # LOGFORMAT = '%(log_color)s%(asctime)s - %(levelname)-8s[%(name)-25s | '\
    #             '%(process)-6d]%(reset)s | %(log_color)s%(message)s%(reset)s'

    logging.root.setLevel(config.DEBUG_LEVEL)

    # formatter = ColoredFormatter(LOGFORMAT)
    # stream = logging.StreamHandler()
    # stream.setLevel(logging.INFO)
    # stream.setFormatter(formatter)

    logger = logging.getLogger('{:15s}'.format(name))
    coloredlogs.install(level='DEBUG', logger=logger)
    # logger.addHandler(stream)
    logger.propagate = False

    return logger


# def msg_to_json(msg, *, status='ok'):
#     data = {'status': status, 'result': msg}
#     return jsonify(data)
#
#
# def wrap_exception(func):
#     @functools.wraps(func)
#     def wrap(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             if config.DEBUG:
#                 traceback.print_exc()
#             return msg_to_json({'error': str(e)}, status='error'), 400
#
#     return wrap
#
#
# def with_lock(func):
#     @functools.wraps(func)
#     def wrap(self, *args, **kwargs):
#         with self._lock:
#             return func(*args, **kwargs)
#
#     return wrap
#
#
# def swag_handler(error, *args):
#     raise Exception(error)
#
#
# def filter_dict(data, keys):
#     return dict((d, data[d]) for d in keys)
