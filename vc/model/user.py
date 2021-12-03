from flask_restplus import fields

from vc.api import api
from vc.db import db
from vc.model.base import BaseModel


class User(db.Model, BaseModel):
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)

    requests = db.relationship('GenerationRequest', backref='user')

    schema = api.model('User', {
        'id': fields.Integer,
        'email': fields.String,
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
    })
