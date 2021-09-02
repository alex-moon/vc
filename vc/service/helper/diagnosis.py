import os
import logging
from hurry.filesize import size
from datetime import datetime

from guppy import hpy


class DiagnosisHelper:
    LOG_FILE_PATH = '/app/data/log'
    hpy = None
    logging = False
    is_debug = False
    last_size = 0

    @classmethod
    def diagnose(cls, description: str):
        if not os.getenv('DEBUG', False):
            return

        if cls.hpy is None:
            cls.hpy = hpy()
            cls.hpy.setref()

        bar = 80 * '='

        heap = cls.hpy.heap()
        last_size = cls.last_size
        current_size = cls.last_size = heap.size
        diff = current_size - last_size
        diff = diff if diff < 0 else '+%s' % diff

        cls.debug(bar)
        cls.debug('DIAGNOSIS:', description.upper())
        cls.debug(bar)
        cls.debug('TOTAL', size(current_size), '(%s b)' % diff)
        cls.debug(bar)
        cls.debug(heap)
        cls.debug(bar)

    @classmethod
    def debug(cls, *args):
        msg = cls.get_message('DEBUG', *args)
        logging.debug(msg)
        if cls.is_debug:
            print(msg)

    @classmethod
    def log(cls, *args):
        msg = cls.get_message('LOG', *args)
        logging.info(msg)
        print(msg)

    @classmethod
    def get_message(cls, tag, *args):
        cls.init()
        return '%s: %s: %s' % (
            datetime.now().isoformat(timespec='seconds'),
            tag,
            ' '.join(map(lambda a: '%s' % a, args))
        )

    @classmethod
    def init(cls):
        cls.is_debug = os.getenv('DEBUG', False)

        if cls.logging is False:
            logging.basicConfig(
                filename=os.path.join(
                    cls.LOG_FILE_PATH,
                    'vc.%s.log' % os.getenv('SERVICE', 'service')
                ),
                level=(
                    logging.DEBUG
                    if cls.is_debug
                    else logging.INFO
                )
            )
            cls.logging = True
