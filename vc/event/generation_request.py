from vc.event.base import VcEvent
from vc.model.generation_request import GenerationRequest


class GenerationRequestCreatedEvent(VcEvent):
    id = 'generation_request.created'
    generation_request: GenerationRequest

    def __init__(self, generation_request: GenerationRequest):
        self.generation_request = generation_request

