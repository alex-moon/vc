from flask_restplus import fields
from sqlalchemy.sql import func

from vc.api import api
from vc.db import db


class GenerationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(
        db.Integer,
        db.ForeignKey('generation_request.id'),
        nullable=False
    )

    url = db.Column(db.String, nullable=False)

    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return '<GenerationResult %r>' % self.id

    schema = api.model('Generation Result', {
        'id': fields.Integer,
        'url': fields.String,
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
    })
