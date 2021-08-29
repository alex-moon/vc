from guppy import hpy
from datetime import datetime


class DiagnosisHelper:
    @classmethod
    def diagnose(cls, description):
        if cls.hpy is None:
            cls.hpy = hpy()
        # rows, columns = os.popen('stty size', 'r').read().split()
        columns = 80
        bar = columns * '='
        now = '%s' % datetime.now()
        print(bar)
        print(now, description)
        print(bar)
        print(now, 'DIAGNOSIS')
        print(bar)
        print(cls.hpy.heap())
        print(bar)
