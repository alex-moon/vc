from typing import Type
from injector import inject

from vc.db import db
from vc.exception import NotFoundException
from vc.event import VcEventDispatcher


class Manager:
    dispatcher: VcEventDispatcher
    model_class: Type[db.Model]

    @inject
    def __init__(self, dispatcher: VcEventDispatcher):
        self.dispatcher = dispatcher

    def all(self):
        return self.model_class.query.all()

    def find_or_throw(self, id_):
        model = self.model_class.query.get(id_)
        if model is None:
            raise NotFoundException(self.model_class.__name__, id_)
        return model

    def create(self, request):
        # @todo ModelFactory.create here

        model = self.model_class(**request.json)
        self.save(model)

        # @todo ModelEventDispatcher.dispatchCreated here

        return model

    def update(self, request, id_):
        model = self.find_or_throw(id_)
        model.__init__(**request.json)
        self.save(model)

        # @todo ModelEventDispatcher.dispatchUpdated here

        return model

    def delete(self, id_):
        model = self.find_or_throw(id_)
        db.session.delete(model)
        self.commit()

    def save(self, model):
        db.session.add(model)
        self.commit()

    def commit(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            # db.session.close()
            pass
