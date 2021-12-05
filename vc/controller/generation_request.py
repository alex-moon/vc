from flask import request
from flask_restplus import fields
from injector import inject
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, \
    Forbidden

from vc.api import api
from vc.auth import auth
from vc.exception import NotFoundException, VcException
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

    @auth.login_required(optional=True)
    def get(self):
        if self.is_god():
            return ns.marshal(self.manager.all(), private_model)
        if self.is_artist():
            return ns.marshal(
                self.manager.mine(self.current_user()),
                private_model
            )
        if self.is_coder():
            return ns.marshal(
                self.manager.mine(self.current_user()),
                public_model
            )
        return ns.marshal(self.manager.published(), public_model)

    @auth.login_required()
    @ns.marshal_with(private_model)
    @ns.expect(post_model, validate=True)
    def post(self):
        try:
            user = self.current_user()
            return self.manager.create_mine(request.json, user)
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

    @auth.login_required()
    def get(self, id_):
        try:
            data = self.manager.find_mine_or_throw(id_, self.current_user())
        except NotFoundException as e:
            raise NotFound(e.message)

        if self.is_artist():
            return ns.marshal(data, private_model)
        return ns.marshal(data, public_model)

    @auth.login_required()
    def delete(self, id_):
        self.manager.delete_mine(id_, self.current_user())
        return {
            "status": True,
        }

    @auth.login_required()
    @ns.marshal_with(private_model)
    def put(self, id_):
        return self.manager.update_mine(id_, request.json, self.current_user())


@ns.route('/<int:id_>/<string:action>')
class GenerationRequestActionController(BaseController):
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

    @auth.login_required()
    @ns.marshal_with(private_model)
    def put(self, id_, action: str):
        if action == 'cancel':
            return self.cancel(id_)
        if action == 'retry':
            return self.retry(id_)
        if action == 'delete':
            return self.soft_delete(id_)
        if action == 'publish':
            return self.publish(id_)
        if action == 'unpublish':
            return self.unpublish(id_)
        raise BadRequest('Unrecognised action: %s' % action)

    def cancel(self, id_):
        return self.manager.cancel(id_, self.current_user())

    def soft_delete(self, id_):
        return self.manager.soft_delete(id_, self.current_user())

    def retry(self, id_):
        return self.manager.retry(id_, self.current_user())

    def publish(self, id_):
        if not self.is_god():
            raise Forbidden()
        return self.manager.publish(id_, self.current_user())

    def unpublish(self, id_):
        if not self.is_god():
            raise Forbidden()
        return self.manager.unpublish(id_, self.current_user())
