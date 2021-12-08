from flask_restplus import Resource

from vc.auth import auth
from vc.manager.user import UserManager
from vc.service.helper.tier import TierHelper


class BaseController(Resource):
    user_manager: UserManager

    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager
        auth.verify_token(self.verify_token)
        auth.get_user_roles(TierHelper.get_user_roles)

    def verify_token(self, token):
        return self.user_manager.authenticate(token)

    def current_user(self):
        return auth.current_user()

    def is_god(self):
        return TierHelper.is_god(self.current_user())

    def is_artist(self):
        return TierHelper.is_artist(self.current_user())

    def is_coder(self):
        return TierHelper.is_coder(self.current_user())

    def is_supporter(self):
        return TierHelper.is_supporter(self.current_user())
