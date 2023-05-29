from vc.event.base import VcEvent
from vc.model.generation_request import GenerationRequest
from vc.model.user import User


class GenerationRequestCreatedEvent(VcEvent):
    id = 'generation_request.created'
    generation_request: GenerationRequest
    user: User

    def __init__(self, generation_request: GenerationRequest, user: User=None):
        self.generation_request = generation_request
        self.user = user


class GenerationRequestCancelledEvent(VcEvent):
    id = 'generation_request.cancelled'
    generation_request: GenerationRequest
    user: User

    def __init__(self, generation_request: GenerationRequest, user: User):
        self.generation_request = generation_request
        self.user = user
