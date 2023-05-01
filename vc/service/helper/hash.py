import bcrypt
import dotenv


class HashHelper:
    @classmethod
    def get(cls, value: str):
        # @todo this is failing
        return bcrypt.hashpw(
            value.encode('utf-8'),
            cls.get_salt(value)
        ).decode()

    @classmethod
    def get_salt(cls, value: str):
        salt = cls.salt_format(dotenv.get_key('.env', 'SALT'))
        hashed = bcrypt.hashpw(
            value.encode('utf-8'),
            salt
        ).decode()
        return cls.salt_format(hashed)

    @classmethod
    def salt_format(cls, value: str):
        return ('$2b$12$%s' % value[-22:]).encode('utf-8')
