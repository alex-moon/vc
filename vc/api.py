from flask_restful import Api

from vc.controller import (
    GenerationRequestController,
    GenerationRequestsController,
    UserController,
    UsersController,
)

api = Api()
api.add_resource(GenerationRequestController, '/generation-request/<int:_id>')
api.add_resource(GenerationRequestsController, '/generation-request')
api.add_resource(UserController, '/user/<int:_id>')
api.add_resource(UsersController, '/user')


# @todo this isn't working, which is really great
# @api.errorhandler
# def default_error_handler(error):
#     return {'message': str(error)}, getattr(error, 'code', 500)
