from flask import request
from flask_restplus import fields
from injector import inject
from werkzeug.exceptions import NotFound, InternalServerError, Forbidden

from vc.auth import auth
from vc.api import api
from vc.exception import NotFoundException, NotAuthenticatedException, VcException
from vc.manager import GenerationRequestManager, UserManager
from vc.model.generation_request import GenerationRequest
from vc.value_object.generation_spec import GenerationSpec
from .base import BaseController

ns = api.namespace(
    'generation-request',
    description='Generation requests'
)

private_model = GenerationRequest.private_schema
public_model = GenerationRequest.public_schema
post_model = ns.model('Generation Request', {
    'spec': fields.Nested(GenerationSpec.schema),
})


@ns.route('/')
class GenerationRequestsController(BaseController):
    manager: GenerationRequestManager

    @inject
    def __init__(
        self,
        user_manager: UserManager,
        manager: GenerationRequestManager,
        *args,
        **kwargs
    ):
        super().__init__(user_manager, *args, **kwargs)
        self.manager = manager

    def get(self):
        data = self.manager.all()
        try:
            auth.current_user()
            return ns.marshal(data, private_model)
        except NotAuthenticatedException:
            return ns.marshal(data, public_model)

    @ns.marshal_with(private_model)
    @ns.expect(post_model, validate=True)
    def post(self):
        try:
            user = auth.current_user()
            return self.manager.create(request.json, user)
        except NotAuthenticatedException as e:
            raise Forbidden(e.message)
        except VcException as e:
            raise InternalServerError(e.message)


@ns.route('/<int:id_>')
class GenerationRequestController(BaseController):
    manager: GenerationRequestManager

    @inject
    def __init__(
        self,
        user_manager: UserManager,
        manager: GenerationRequestManager,
        *args,
        **kwargs
    ):
        super().__init__(user_manager, *args, **kwargs)
        self.manager = manager

    def get(self, id_):
        try:
            data = self.manager.find_or_throw(id_)
        except NotFoundException as e:
            raise NotFound(e.message)
        try:
            auth.current_user()
            return ns.marshal(data, private_model)
        except NotAuthenticatedException:
            return ns.marshal(data, public_model)

    def delete(self, id_):
        try:
            auth.current_user()
            self.manager.delete(id_)
        except NotAuthenticatedException as e:
            raise Forbidden(e.message)
        return {
            "status": True,
        }

    @ns.marshal_with(private_model)
    def put(self, id_):
        try:
            auth.current_user()
            return self.manager.update(id_, request.json)
        except NotAuthenticatedException as e:
            raise Forbidden(e.message)
