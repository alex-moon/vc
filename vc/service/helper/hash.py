import bcrypt
import os
import hashlib
import base64


class HashHelper:
    @classmethod
    def get(cls, value: str):
        salt = cls.get_salt(value)
        return bcrypt.hashpw(
            value.encode('utf-8'),
            salt
        ).decode()

    @classmethod
    def get_salt(cls, unique_input: str):
        secret_key = os.getenv('APP_KEY')

        hmac_obj = hashlib.sha256(secret_key.encode('utf-8'))
        hmac_obj.update(unique_input.encode('utf-8'))
        hmac_digest = hmac_obj.digest()

        salt_value = base64.b64encode(hmac_digest)[:22]
        return ('$2b$12$%s' % salt_value.decode('utf-8')).encode('utf-8')
