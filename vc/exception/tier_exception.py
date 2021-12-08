from .vc_exception import VcException


class TierException(VcException):
    code = 403

    def __init__(self, tier: str, info: str = None):
        message = "Minimum tier required: [%s]" % tier
        if info is not None:
            message += ': %s' % info
        super().__init__(message)
