from vc.db import db
from vc.manager.base import Manager
from vc.model.user import User
from vc.service.helper.hash import HashHelper


class UserManager(Manager):
    model_class = User

    def authenticate(self, token):
        try:
            hashed = HashHelper.get(token)
            return self.model_class.query.filter(
                self.model_class.deleted.__eq__(None),
                self.model_class.token.__eq__(hashed)
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e
