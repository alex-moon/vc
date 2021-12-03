from flask_restplus import Resource

from vc.manager.user import UserManager
from vc.auth import auth
from vc.model.user import UserTier


class BaseController(Resource):
    user_manager: UserManager

    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager
        auth.verify_token(self.verifyToken)
        auth.get_user_roles(self.getUserRoles)

    def verifyToken(self, token):
        return self.user_manager.authenticate(token)

    def getUserRoles(self, user):
        result = []
        i = user.tier
        while i > 0:
            result.append(i)
            i -= 1
        return result

    def currentUser(self):
        return auth.current_user()

    def isGod(self):
        return self.isTier(UserTier.God)

    def isArtist(self):
        return self.isTier(UserTier.Artist)

    def isCoder(self):
        return self.isTier(UserTier.Coder)

    def isSupporter(self):
        return self.currentUser().tier is not None

    def isTier(self, value):
        return value in self.getUserRoles(self.currentUser())
