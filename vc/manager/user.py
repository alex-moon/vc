from vc.db import db
from vc.exception import NotAuthenticatedException
from vc.manager.base import Manager
from vc.model.user import User


class UserManager(Manager):
    model_class = User

    def authenticate_or_throw(self, token):
        try:
            model = self.model_class.query.filter(
                self.model_class.deleted.__eq__(None),
                self.model_class.token.__eq__(token)
            ).first()
            if model is None:
                raise NotAuthenticatedException(token)
            return model
        except Exception as e:
            db.session.rollback()
            raise e
