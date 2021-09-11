from flask import request
from flask_restplus import Resource, fields
from injector import inject
from werkzeug.exceptions import NotFound, InternalServerError

from vc.api import api
from vc.exception import NotFoundException, VcException
from vc.manager import GenerationRequestManager
from vc.model.generation_request import GenerationRequest
from vc.value_object.generation_spec import GenerationSpec

ns = api.namespace(
    'generation-request',
    description='Generation requests'
)

model = GenerationRequest.schema
post_model = ns.model('Generation Request', {
    'spec': fields.Nested(GenerationSpec.schema),
})


@ns.route('/')
class GenerationRequestsController(Resource):
    @inject
    def __init__(
        self,
        manager: GenerationRequestManager,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.manager = manager

    @ns.marshal_list_with(model)
    def get(self):
        return self.manager.all()

    @ns.marshal_with(model)
    @ns.expect(post_model, validate=True)
    def post(self):
        try:
            return self.manager.create(request.json)
        except VcException as e:
            raise InternalServerError(e.message)


@ns.route('/<int:id_>')
class GenerationRequestController(Resource):
    @inject
    def __init__(
        self,
        manager: GenerationRequestManager,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.manager = manager

    @ns.marshal_with(model)
    def get(self, id_):
        try:
            return self.manager.find_or_throw(id_)
        except NotFoundException as e:
            raise NotFound(e.message)

    def delete(self, id_):
        self.manager.delete(id_)
        return {
            "status": True,
        }

    @ns.marshal_with(model)
    def put(self, id_):
        return self.manager.update(id_, request.json)
