from flask_restplus import Resource

from vc.manager.user import UserManager
from vc.auth import auth
from vc.model.user import UserTier


class BaseController(Resource):
    user_manager: UserManager

    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager
        auth.verify_token(self.verify_token)
        auth.get_user_roles(self.get_user_roles)

    def verify_token(self, token):
        return self.user_manager.authenticate(token)

    def get_user_roles(self, user):
        result = []
        i = user.tier
        while i > 0:
            result.append(i)
            i -= 1
        return result

    def current_user(self):
        return auth.current_user()

    def is_god(self):
        return self.is_tier(UserTier.God)

    def is_artist(self):
        return self.is_tier(UserTier.Artist)

    def is_coder(self):
        return self.is_tier(UserTier.Coder)

    def is_supporter(self):
        return self.current_user().tier is not None

    def is_tier(self, value):
        return value in self.getUserRoles(self.current_user())
