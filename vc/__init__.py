from dotenv import dotenv_values
from flask import Flask
from flask_injector import FlaskInjector

from .api import api
from .db import db
from .q import q
from .injector import injector
from .services import modules
from .controller import init_app


def fix_bug(app):
    # @see https://stackoverflow.com/questions/67629887/flaskinjector-runtimeerror-working-outside-of-request-context-with-flask-2-0
    app.jinja_env.globals = {}


def create_app():
    # initialise the app
    app = Flask(__name__)
    config = dict(dotenv_values())
    app.config.update(config)
    fix_bug(app)

    # spin everything up
    api.init_app(app)
    db.init_app(app)
    controller.init_app(app)
    q.init_app(app)
    app.app_context().push()
    db.create_all()
    FlaskInjector(app=app, modules=modules, injector=injector)
    return app
