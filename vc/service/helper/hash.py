import bcrypt


class HashHelper:
    @classmethod
    def get(cls, value: str):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(value.encode('utf-8'), salt)

    @classmethod
    def check(cls, candidate: str, value: str):
        return bcrypt.checkpw(candidate.encode('utf-8'), value)
