from datetime import datetime

from vc.model.generation_request import GenerationRequest
from vc.event import GenerationRequestCreatedEvent, GenerationRequestCancelledEvent
from vc.manager.base import Manager
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

    def create(self, request, user: User = None):
        model = super().create(request, user)

        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        self.save(model)

        return model

    def cancel(self, id_):
        model = super().find_or_throw(id_)
        model.cancelled = datetime.now()
        model.retried = None

        self.dispatcher.dispatch(
            GenerationRequestCancelledEvent(model)
        )

        self.save(model)

        return model

    def soft_delete(self, id_):
        model = super().find_or_throw(id_)
        model.deleted = datetime.now()

        self.save(model)

        return model

    def retry(self, id_):
        model = super().find_or_throw(id_)
        model.retried = datetime.now()
        model.cancelled = None

        # @todo technically should be a different event
        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        self.save(model)

        return model
