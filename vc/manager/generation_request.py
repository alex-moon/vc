from datetime import datetime

from vc.db import db
from vc.event import (
    GenerationRequestCreatedEvent,
    GenerationRequestCancelledEvent
)
from vc.exception import NotFoundException
from vc.manager.base import Manager
from vc.model.generation_request import GenerationRequest
from vc.model.user import User


class GenerationRequestManager(Manager):
    model_class = GenerationRequest

    def published_query(self):
        return self.all_query().filter(
            self.model_class.published.__ne__(None)
        )

    def published(self):
        try:
            return self.published_query().all()
        except Exception as e:
            db.session.rollback()
            raise e

    def mine_query(self, user: User):
        return self.all_query().filter(
            self.model_class.user_id.__eq__(user.id)
        )

    def mine(self, user: User):
        try:
            return self.mine_query(user).all()
        except Exception as e:
            db.session.rollback()
            raise e

    def find_mine_or_throw(self, id_, user: User):
        try:
            model = self.mine_query(user).get(id_)
            if model is None:
                raise NotFoundException(self.model_class.__name__, id_)
            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def create_mine(self, request, user: User):
        model = super().create(request)
        model.user_id = user.id

        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        self.save(model)

        return model

    def update_mine(self, id_, raw, user: User):
        try:
            model = self.find_mine_or_throw(id_, user)
            model.__init__(**self.fields(raw))
            self.save(model)

            # @todo ModelEventDispatcher.dispatchUpdated here

            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_mine(self, id_, user: User):
        try:
            model = self.find_mine_or_throw(id_, user)
            db.session.delete(model)
            self.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def cancel(self, id_, user: User):
        model = self.find_mine_or_throw(id_, user)
        model.cancelled = datetime.now()

        self.dispatcher.dispatch(
            GenerationRequestCancelledEvent(model)
        )

        self.save(model)

        return model

    def soft_delete(self, id_, user: User):
        model = self.find_mine_or_throw(id_, user)
        model.deleted = datetime.now()

        self.save(model)

        return model

    def retry(self, id_, user: User):
        model = self.find_mine_or_throw(id_, user)
        model.retried = datetime.now()

        # @todo technically should be a different event
        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        self.save(model)

        return model

    def publish(self, id_, user: User):
        model = self.find_mine_or_throw(id_, user)
        model.published = datetime.now()

        self.save(model)

        return model

    def unpublish(self, id_, user: User):
        model = self.find_mine_or_throw(id_, user)
        model.published = None

        self.save(model)

        return model
