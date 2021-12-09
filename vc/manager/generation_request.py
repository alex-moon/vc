from datetime import datetime
from sqlalchemy import or_

from vc.db import db
from vc.event import (
    GenerationRequestCreatedEvent,
    GenerationRequestCancelledEvent
)
from vc.exception import NotFoundException
from vc.manager.base import Manager
from vc.model.generation_request import GenerationRequest
from vc.model.user import User
from vc.service.helper.tier import TierHelper


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

    def mine_queued(self, user: User):
        try:
            return self.mine_query(user).filter(
                self.model_class.completed.__eq__(None),
                or_(
                    self.model_class.cancelled.__eq__(None),
                    self.model_class.cancelled.__lt__(
                        self.model_class.retried
                    )
                ),
                self.model_class.deleted.__eq__(None),
            ).all()
        except Exception as e:
            db.session.rollback()
            raise e

    def find_or_throw(self, id_, user: User = None):
        try:
            model = (
                self.all_query()
                if user is None or TierHelper.is_god(user)
                else self.mine_query(user)
            ).filter(
                self.model_class.id.__eq__(id_)
            ).first()
            if model is None:
                raise NotFoundException(self.model_class.__name__, id_)
            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def create(self, raw, user: User = None):
        try:
            # @todo ModelFactory.create here

            model = self.model_class(**self.fields(raw, user))
            model.user_id = user.id
            self.save(model)

            self.dispatcher.dispatch(
                GenerationRequestCreatedEvent(model, user)
            )

            return model
        except Exception as e:
            db.session.rollback()
            raise e

    def cancel(self, id_, user: User):
        model = self.find_or_throw(id_, user)
        model.cancelled = datetime.now()

        self.dispatcher.dispatch(
            GenerationRequestCancelledEvent(model, user)
        )

        self.save(model)

        return model

    def soft_delete(self, id_, user: User):
        model = self.find_or_throw(id_, user)
        model.deleted = datetime.now()

        self.save(model)

        return model

    def retry(self, id_, user: User):
        model = self.find_or_throw(id_, user)
        model.retried = datetime.now()

        # @todo technically should be a different event
        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model, user)
        )

        self.save(model)

        return model

    def publish(self, id_, user: User):
        model = self.find_or_throw(id_, user)
        model.published = datetime.now()

        self.save(model)

        return model

    def unpublish(self, id_, user: User):
        model = self.find_or_throw(id_, user)
        model.published = None

        self.save(model)

        return model
