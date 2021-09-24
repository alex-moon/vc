from .vc_exception import VcException


class NotAuthenticatedException(VcException):
    code = 403

    def __init__(self, token: str):
        super().__init__("Invalid token: [%s]" % token)
