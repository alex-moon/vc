from datetime import datetime

from vc.model.generation_request import GenerationRequest
from vc.event import GenerationRequestCreatedEvent
from vc.manager.base import Manager
from vc.model.user import User


class GenerationRequestManager(Manager):
    model_class = GenerationRequest

    def create(self, request, user: User = None):
        model = super().create(request, user)

        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        return model

    def cancel(self, id_):
        model = super().find_or_throw(id_)
        model.cancelled = datetime.now()
        super().save(model)

    def soft_delete(self, id_):
        model = super().find_or_throw(id_)
        model.deleted = datetime.now()
        super().save(model)
