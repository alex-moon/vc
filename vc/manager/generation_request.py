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
