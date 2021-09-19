from flask_restplus import fields
from sqlalchemy.sql import func

from vc.api import api
from vc.db import db
from vc.model.base import BaseModel


class GenerationResult(db.Model, BaseModel):
    request_id = db.Column(
        db.Integer,
        db.ForeignKey('generation_request.id'),
        nullable=False
    )

    url = db.Column(db.String, nullable=False)

    schema = api.model('Generation Result', {
        'id': fields.Integer,
        'url': fields.String,
        'created': fields.DateTime(),
        'updated': fields.DateTime(),
        'deleted': fields.DateTime(),
    })
