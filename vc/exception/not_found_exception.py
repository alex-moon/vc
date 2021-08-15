from .vc_exception import VcException


class NotFoundException(VcException):
    code = 404

    def __init__(self, model_class: str, id_: int):
        super().__init__("Model not found: [%s] for id [%s]" % (model_class, id_))
