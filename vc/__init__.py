import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector

from .api import api
from .controller import init_app
from .db import db
from .migrate import migrate
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@%s:%s/%s' % (
        app.config['DB_USER'],
        app.config['DB_PASS'],
        app.config['DB_HOST'],
        app.config['DB_PORT'],
        app.config['DB_NAME'],
    )
    app.config['RQ_DEFAULT_URL'] = 'redis://:%s@%s:%s/1' % (
        app.config['REDIS_PASS'],
        app.config['REDIS_HOST'],
        app.config['REDIS_PORT'],
    )

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # spin everything up
    api.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    controller.init_app(app)
    q.init_app(app)
    app.app_context().push()
    db.create_all()
    FlaskInjector(app=app, modules=modules, injector=injector)
    return app
