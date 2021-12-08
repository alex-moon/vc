from flask import request
from flask_restplus import fields
from werkzeug.exceptions import NotFound, InternalServerError
from injector import inject

from vc.api import api
from vc.auth import auth
from vc.exception import NotFoundException, VcException
from vc.model.user import User, UserTier
from .base import BaseController
from ..manager import UserManager

ns = api.namespace(
    'user',
    description='User'
)

model = User.schema
post_model = ns.model('User', {
    'email': fields.String,
    'name': fields.String,
    'tier': fields.Integer,
})


@ns.route('/')
class UsersController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required(role=UserTier.God)
    def get(self):
        return ns.marshal(self.user_manager.all(), model)

    @auth.login_required(role=UserTier.God)
    @ns.marshal_with(model)
    @ns.expect(post_model, validate=True)
    def post(self):
        try:
            return self.user_manager.create(request.json, self.current_user())
        except VcException as e:
            raise InternalServerError(e.message)


@ns.route('/<int:id_>')
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

        return ns.marshal(data, model)

    @auth.login_required(role=UserTier.God)
    def delete(self, id_):
        self.user_manager.delete(id_, self.current_user())
        return {
            "status": True,
        }

    @auth.login_required(role=UserTier.God)
    @ns.marshal_with(model)
    def put(self, id_):
        return self.user_manager.update(id_, request.json, self.current_user())


@ns.route('/<int:id_>/token')
class UserTokenController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required(role=UserTier.God)
    @ns.marshal_with(model)
    def put(self, id_):
        return self.user_manager.regenerate_token(id_)


@ns.route('/me')
class MeController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required()
    def get(self):
        return ns.marshal(self.current_user(), model)

    @auth.login_required()
    @ns.marshal_with(model)
    def put(self):
        return self.user_manager.update(
            self.current_user().id,
            request.json,
            self.current_user()
        )


@ns.route('/me/token')
class MeTokenController(BaseController):
    @inject
    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(user_manager, *args, **kwargs)

    @auth.login_required()
    @ns.marshal_with(model)
    def put(self):
        return self.user_manager.regenerate_token(self.current_user().id)
