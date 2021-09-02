import logging
import os
from datetime import datetime

from guppy import hpy
from hurry.filesize import size


class DiagnosisHelper:
    LOG_FILE_PATH = '/opt/vc/log'
    hpy = None
    logging = False
    is_debug = False
    last_size = {
        'REACHABLE': 0,
        'UNREACHABLE': 0,
    }
    refset = False

    @classmethod
    def diagnose(cls, *args, short=False, setref=True):
        if not os.getenv('DEBUG', False):
            return

        if cls.hpy is None:
            cls.hpy = hpy()
            cls.hpy.setref()

        if setref and not cls.refset:
            cls.hpy.setref()
            cls.refset = True

        bar = 80 * '='

        reachable = cls.hpy.heap()
        reachable_summary = cls.get_size_summary(reachable, 'REACHABLE')

        description = ' '.join(map(lambda a: '%s' % a, args))

        if short:
            cls.debug('DIAGNOSIS:', description.upper(), reachable_summary)
            return

        biggest_object = reachable.byid[0]

        cls.debug(bar)
        cls.debug('DIAGNOSIS:', description.upper())
        cls.debug(bar)
        cls.debug('TOTAL', reachable_summary)
        cls.debug(bar)
        cls.debug(reachable)
        cls.debug(bar)
        cls.debug(
            'BIGGEST OBJECT',
            size(biggest_object.size),
            biggest_object,
            biggest_object.sp
        )
        cls.debug(bar)

    @classmethod
    def get_size_summary(cls, heap, key):
        last_size = cls.last_size[key]
        current_size = cls.last_size[key] = heap.size
        diff = current_size - last_size

        if diff > 100 * 1024 * 1024:
            # import ipdb;ipdb.set_trace()
            pass

        diff = (
            '-%s' % size(abs(diff))
            if diff < 0
            else '+%s' % size(diff)
        )
        return '%s (%s)' % (size(current_size), diff)

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
                    'vc.%s.diagnosis.log' % os.getenv('SERVICE', 'service')
                ),
                level=(
                    logging.DEBUG
                    if cls.is_debug
                    else logging.INFO
                )
            )
            cls.logging = True
