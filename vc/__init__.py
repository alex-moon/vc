import os

from dotenv import load_dotenv
from flask import Flask
from flask_injector import FlaskInjector

from .api import api
from .controller import init_app
from .db import db
from .injector import injector
from .q import q
from .services import modules


def create_app():
    # initialise os.environ
    load_dotenv(override=True)

    # initialise the app
    app = Flask(__name__)
    app.config.update(os.environ)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

    # spin everything up
    api.init_app(app)
    db.init_app(app)
    controller.init_app(app)
    q.init_app(app)
    app.app_context().push()
    db.create_all()
    FlaskInjector(app=app, modules=modules, injector=injector)
    return app
