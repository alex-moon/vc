from flask_restful import fields

from vc.db import db
from vc.model.base import BaseModel


class UserTier:
    Supporter = 0
    Coder = 1
    Artist = 2
    God = 3


class User(db.Model, BaseModel):
    FIELDS = [
        'name',
        'email',
    ]
    GOD_FIELDS = [
        'tier',
    ]

    api_token: str = None

    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    tier = db.Column(db.Integer, nullable=False, default=0)

    requests = db.relationship('GenerationRequest', backref='user')

    schema = {
        'id': fields.Integer,
        'email': fields.String,
        'name': fields.String,
        'api_token': fields.String,
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
    }
