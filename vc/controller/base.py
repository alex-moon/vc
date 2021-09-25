from flask_restplus import Resource

from vc.manager.user import UserManager
from vc.auth import auth


class BaseController(Resource):
    user_manager: UserManager

    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager
        auth.verify_token(self.verify_token)

    def verify_token(self, token):
        return self.user_manager.authenticate_or_throw(token)
