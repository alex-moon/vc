from flask_restplus import fields

from vc.api import api
from vc.db import db
from vc.model.base import BaseModel
from vc.model.generation_result import GenerationResult
from vc.value_object.generation_spec import GenerationSpec


class GenerationRequest(db.Model, BaseModel):
    spec = db.Column(db.JSON, nullable=False)

    started = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    failed = db.Column(db.DateTime)

    steps_completed = db.Column(db.Integer)
    steps_total = db.Column(db.Integer)

    name = db.Column(db.String, nullable=True)
    preview = db.Column(db.String, nullable=True)
    interim = db.Column(db.String, nullable=True)

    results = db.relationship('GenerationResult', backref='request')

    schema = api.model('Generation Request', {
        'id': fields.Integer,
        'spec': fields.Nested(GenerationSpec.schema),
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
        'started': fields.DateTime(),
        'completed': fields.DateTime(),
        'failed': fields.DateTime(),
        'steps_completed': fields.Integer,
        'steps_total': fields.Integer,
        'name': fields.String,
        'preview': fields.String,
        'interim': fields.String,
        'results': fields.List(fields.Nested(GenerationResult.schema)),
    })
