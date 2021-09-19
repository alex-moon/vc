from sqlalchemy.sql import func

from vc.db import db


class BaseModel:
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.id)
