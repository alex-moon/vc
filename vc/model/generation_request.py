from flask_restplus import fields

from vc.api import api
from vc.db import db
from vc.model.base import BaseModel
from vc.model.generation_result import GenerationResult
from vc.value_object.generation_spec import GenerationSpec


class GenerationRequest(db.Model, BaseModel):
    FIELDS = [
        'spec',
    ]
    GOD_FIELDS = [
        'steps_completed',
    ]

    spec = db.Column(db.JSON, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    started = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    failed = db.Column(db.DateTime)
    cancelled = db.Column(db.DateTime)
    retried = db.Column(db.DateTime)
    published = db.Column(db.DateTime)

    steps_completed = db.Column(db.Integer)
    steps_total = db.Column(db.Integer)

    name = db.Column(db.String)
    hash = db.Column(db.String)

    preview = db.Column(db.String)
    interim = db.Column(db.String)
    interim_watermarked = db.Column(db.String)

    results = db.relationship('GenerationResult', backref='request')

    private_schema = api.model('Generation Request', {
        'id': fields.Integer,
        'spec': fields.Nested(GenerationSpec.schema),
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
        'started': fields.DateTime(),
        'completed': fields.DateTime(),
        'failed': fields.DateTime(),
        'cancelled': fields.DateTime(),
        'retried': fields.DateTime(),
        'published': fields.DateTime(),
        'steps_completed': fields.Integer,
        'steps_total': fields.Integer,
        'name': fields.String,
        'preview': fields.String,
        'interim': fields.String,
        'interim_watermarked': fields.String,
        'results': fields.List(fields.Nested(GenerationResult.public_schema)),
    })

    public_schema = api.model('Generation Request', {
        'id': fields.Integer,
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
        'started': fields.DateTime(),
        'completed': fields.DateTime(),
        'failed': fields.DateTime(),
        'cancelled': fields.DateTime(),
        'retried': fields.DateTime(),
        'steps_completed': fields.Integer,
        'steps_total': fields.Integer,
        'name': fields.String,
        'preview': fields.String,
        'interim_watermarked': fields.String,
        'results': fields.List(fields.Nested(GenerationResult.private_schema)),
    })
