from flask import request
from flask_restful import fields, marshal, marshal_with
from werkzeug.exceptions import NotFound, InternalServerError
from injector import inject

from vc.auth import auth
from vc.exception import NotFoundException, VcException
from vc.model.user import User, UserTier
from .base import BaseController
from ..manager import UserManager


model = User.schema
post_model = {
    'email': fields.String,
    'name': fields.String,
    'tier': fields.Integer,
}


class UsersController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required(role=UserTier.God)
    def get(self):
        return marshal(self.user_manager.all(), model)

    @auth.login_required(role=UserTier.God)
    @marshal_with(model)
    # @expect(post_model, validate=True)
    def post(self):
        try:
            return self.user_manager.create(request.json, self.current_user())
        except VcException as e:
            raise InternalServerError(e.message)


class UserController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required(role=UserTier.God)
    def get(self, id_):
        try:
            data = self.user_manager.find_or_throw(id_, self.current_user())
        except NotFoundException as e:
            raise NotFound(e.message)

        return marshal(data, model)

    @auth.login_required(role=UserTier.God)
    def delete(self, id_):
        self.user_manager.delete(id_, self.current_user())
        return {
            "status": True,
        }

    @auth.login_required(role=UserTier.God)
    @marshal_with(model)
    def put(self, id_):
        return self.user_manager.update(id_, request.json, self.current_user())


class UserTokenController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required(role=UserTier.God)
    @marshal_with(model)
    def put(self, id_):
        return self.user_manager.regenerate_token(id_)


class MeController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required()
    def get(self):
        return marshal(self.current_user(), model)

    @auth.login_required()
    @marshal_with(model)
    def put(self):
        return self.user_manager.update(
            self.current_user().id,
            request.json,
            self.current_user()
        )


class MeTokenController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required()
    @marshal_with(model)
    def put(self):
        return self.user_manager.regenerate_token(self.current_user().id)
