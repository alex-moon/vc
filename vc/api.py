from flask import jsonify
from flask_restful import Api
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException

from vc.controller import (
    GenerationRequestController,
    GenerationRequestsController,
    MeController,
    MeTokenController,
    UserController,
    UsersController,
    UserTokenController,
    GenerationRequestActionController,
)

class VcApi(Api):
    def handle_error(self, err):
        print(err)

        if isinstance(err, HTTPException):
            return jsonify({
                'message': getattr(
                    err,
                    'description',
                    HTTP_STATUS_CODES.get(err.code, '')
                )
            }), err.code

        # if not getattr(err, 'message', None):
        #     return jsonify({
        #         'message': 'Server has encountered some error'
        #     }), 500

        return jsonify(**err.kwargs), err.http_status_code

api = VcApi()
api.add_resource(GenerationRequestController, '/generation-request/<int:id_>')
api.add_resource(GenerationRequestActionController, '/generation-request/<int:id_>/<string:action>')
api.add_resource(GenerationRequestsController, '/generation-request')
api.add_resource(MeController, '/user/me')
api.add_resource(MeTokenController, '/user/me/token')
api.add_resource(UserController, '/user/<int:id_>')
api.add_resource(UserTokenController, '/user/<int:id_>/token')
api.add_resource(UsersController, '/user')
