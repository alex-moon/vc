from datetime import datetime

from guppy import hpy


class DiagnosisHelper:
    hpy = None

    @classmethod
    def diagnose(cls, description: str):
        if cls.hpy is None:
            cls.hpy = hpy()
            cls.hpy.setref()
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
