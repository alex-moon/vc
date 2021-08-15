class VcException(Exception):
    message = "An error occurred"

    def __init__(self, message: str = None):
        super().__init__()
        if message is not None:
            self.message = message

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message

    @classmethod
    def for_exception(cls, e: Exception):
        return cls(getattr(e, 'message', str(e)))
