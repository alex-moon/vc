from sqlalchemy.sql import func

from vc.db import db


class GenerationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spec = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    started = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    failed = db.Column(db.DateTime)

    def __repr__(self):
        return '<GenerationRequest %r>' % self.id
