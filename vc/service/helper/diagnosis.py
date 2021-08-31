import os
import logging
from datetime import datetime

from guppy import hpy


class DiagnosisHelper:
    LOG_FILE_PATH = '/var/log/vc'
    hpy = None
    logging = False
    is_debug = False

    @classmethod
    def diagnose(cls, description: str):
        if not os.getenv('DEBUG', False):
            return

        bar = 80 * '='

        if cls.hpy is None:
            cls.hpy = hpy()
            cls.debug(bar)
            cls.debug('PRE SETREF DIAGNOSIS')
            cls.debug(bar)
            cls.debug(cls.hpy.heap())
            cls.debug(bar)
            cls.hpy.setref()

        cls.debug(bar)
        cls.debug('DIAGNOSIS:', description.upper())
        cls.debug(bar)
        cls.debug(cls.hpy.heap())
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
