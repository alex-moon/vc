from typing import Type

from injector import inject

from vc.db import db
from vc.event import VcEventDispatcher
from vc.exception import NotFoundException
from vc.model.user import User
from vc.service.helper.tier import TierHelper


class Manager:
    dispatcher: VcEventDispatcher
    model_class: Type[db.Model]

    @inject
    def __init__(self, dispatcher: VcEventDispatcher):
        self.dispatcher = dispatcher

    def all_query(self):
        return self.model_class.query.filter(
            self.model_class.deleted.__eq__(None)
        ).order_by(
            self.model_class.created.desc()
        )

    def all(self):
        try:
            return self.all_query().all()
        except Exception as e:
            db.session.rollback()
            raise e

    def find_or_throw(self, id_, user: User):
        try:
            model = self.model_class.query.get(id_)
            if model is None:
                raise NotFoundException(self.model_class.__name__, id_)
            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def create(self, raw, user: User):
        try:
            # @todo ModelFactory.create here

            model = self.model_class(**self.fields(raw, user))
            self.save(model)

            # @todo ModelEventDispatcher.dispatchCreated here

            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, id_, raw, user: User):
        try:
            model = self.find_or_throw(id_, user)
            model.__init__(**self.fields(raw, user))
            self.save(model)

            # @todo ModelEventDispatcher.dispatchUpdated here

            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self, id_, user: User):
        try:
            model = self.find_or_throw(id_, user)
            db.session.delete(model)
            self.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def save(self, model):
        try:
            db.session.add(model)
            self.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def commit(self):
        db.session.commit()

    def fields(self, raw, user: User):
        fields = self.model_class.FIELDS
        if TierHelper.is_god(user):
            fields += self.model_class.GOD_FIELDS
        return {k: raw[k] for k in raw.keys() & fields}
