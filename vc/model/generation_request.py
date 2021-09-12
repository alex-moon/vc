from flask_restplus import fields
from sqlalchemy.sql import func

from vc.api import api
from vc.db import db
from vc.model.generation_result import GenerationResult
from vc.value_object.generation_spec import GenerationSpec


class GenerationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spec = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    started = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    failed = db.Column(db.DateTime)

    steps_completed = db.Column(db.Integer)
    steps_total = db.Column(db.Integer)

    name = db.Column(db.String, nullable=True)
    preview = db.Column(db.String, nullable=True)

    results = db.relationship('GenerationResult', backref='request')

    def __repr__(self):
        return '<GenerationRequest %r>' % self.id

    schema = api.model('Generation Request', {
        'id': fields.Integer,
        'spec': fields.Nested(GenerationSpec.schema),
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'started': fields.DateTime(),
        'completed': fields.DateTime(),
        'failed': fields.DateTime(),
        'steps_completed': fields.Integer,
        'steps_total': fields.Integer,
        'name': fields.String,
        'preview': fields.String,
        'results': fields.List(fields.Nested(GenerationResult.schema)),
    })
