from flask import request
from flask_restplus import fields
from injector import inject
from werkzeug.exceptions import NotFound, InternalServerError, Forbidden

from vc.api import api
from vc.auth import auth
from vc.exception import NotFoundException, VcException
from vc.manager import UserManager
from vc.model.user import User, UserTier
from .base import BaseController

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
    manager: UserManager

    @inject
    def __init__(
        self,
        user_manager: UserManager,
        manager: UserManager,
        *args,
        **kwargs
    ):
        super().__init__(user_manager, *args, **kwargs)
        self.manager = manager

    @auth.login_required(role=UserTier.God)
    def get(self):
        return ns.marshal(self.manager.all(), model)

    @auth.login_required(role=UserTier.God)
    @ns.marshal_with(model)
    @ns.expect(post_model, validate=True)
    def post(self):
        try:
            return self.manager.create(request.json)
        except VcException as e:
            raise InternalServerError(e.message)


@ns.route('/<int:id_>')
class UserController(BaseController):
    manager: UserManager

    @inject
    def __init__(
        self,
        user_manager: UserManager,
        manager: UserManager,
        *args,
        **kwargs
    ):
        super().__init__(user_manager, *args, **kwargs)
        self.manager = manager

    @auth.login_required(role=UserTier.God)
    def get(self, id_):
        try:
            data = self.manager.find_or_throw(id_)
        except NotFoundException as e:
            raise NotFound(e.message)

        return ns.marshal(data, model)

    @auth.login_required(role=UserTier.God)
    def delete(self, id_):
        self.manager.delete(id_)
        return {
            "status": True,
        }

    @auth.login_required(role=UserTier.God)
    @ns.marshal_with(model)
    def put(self, id_):
        return self.manager.update(id_, request.json)


@ns.route('/me')
class MeController(BaseController):
    manager: UserManager

    @inject
    def __init__(
        self,
        user_manager: UserManager,
        manager: UserManager,
        *args,
        **kwargs
    ):
        super().__init__(user_manager, *args, **kwargs)
        self.manager = manager

    @auth.login_required()
    def get(self):
        return ns.marshal(self.current_user(), model)

    @auth.login_required()
    @ns.marshal_with(model)
    def put(self):
        return self.manager.update(self.current_user().id, request.json)
