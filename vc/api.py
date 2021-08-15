from flask_restplus import Api

api = Api()


# @todo this isn't working, which is really great
# @api.errorhandler
# def default_error_handler(error):
#     return {'message': str(error)}, getattr(error, 'code', 500)
