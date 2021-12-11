from vc.model.user import User, UserTier


class TierHelper:
    INTERIM_STEPS = 60

    @classmethod
    def get_user_roles(cls, user):
        result = []
        i = user.tier
        while i >= 0:
            result.append(i)
            i -= 1
        return result

    @classmethod
    def is_tier(cls, user: User, value):
        if user is None:
            return False
        return value in cls.get_user_roles(user)

    @classmethod
    def is_god(cls, user: User):
        return cls.is_tier(user, UserTier.God)

    @classmethod
    def is_artist(cls, user: User):
        return cls.is_tier(user, UserTier.Artist)

    @classmethod
    def is_coder(cls, user: User):
        return cls.is_tier(user, UserTier.Coder)

    @classmethod
    def is_supporter(cls, user: User):
        return cls.is_tier(user, UserTier.Supporter)
