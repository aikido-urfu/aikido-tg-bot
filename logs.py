import sys
import os
import logging
from logging.handlers import RotatingFileHandler

get_trace = getattr(sys, 'gettrace', None)
log_file_name = 'storage/logs/bot.log'
file_handlers = (RotatingFileHandler(log_file_name, backupCount=20, maxBytes=2000000, encoding='utf-8'),)

if get_trace is None:
    print('No sys.gettrace')
elif get_trace():
    log_file_name = ''
    file_handlers = None

# TODO: https://betterstack.com/community/guides/logging/how-to-start-logging-with-python/
# def keep_log_size():
#     f = open('logs/bot.log')
#     _l = len(f.readlines())
#     f.close()
#     if _l >= 10000:
#         os.rename('logs/bot.log', newName)


logging.basicConfig(level=logging.INFO,
                    # filename=log_file_name,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format="%(name)s %(asctime)s %(levelname)s %(message)s",
                    # encoding='utf-8',
                    handlers=file_handlers)


logging.info(f'{"-" * 47}bot started{"-" * 47}')
