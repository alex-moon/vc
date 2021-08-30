from guppy import hpy
from datetime import datetime


class DiagnosisHelper:
    hpy = None

    @classmethod
    def diagnose(cls, description: str):
        if cls.hpy is None:
            cls.hpy = hpy()
        # rows, columns = os.popen('stty size', 'r').read().split()
        columns = 80
        bar = columns * '='
        now = '%s' % datetime.now()
        print(bar)
        print(now, 'DIAGNOSIS')
        print(bar)
        print(now, description.upper())
        print(bar)
        print(cls.hpy.heap())
        print(bar)
