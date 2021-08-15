from vc.model.generation_request import GenerationRequest
from vc.event import GenerationRequestCreatedEvent
from vc.manager.base import Manager


class GenerationRequestManager(Manager):
    model_class = GenerationRequest

    def create(self, request):
        model = super().create(request)

        self.dispatcher.dispatch(
            GenerationRequestCreatedEvent(model)
        )

        return model
