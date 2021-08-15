from datetime import datetime
from injector import inject

from vc.value_object import GenerationSpec
from vc.manager.generation_request import GenerationRequestManager
from vc.model.generation_request import GenerationRequest
from vc.service.generation import GenerationService
from vc.job.base import Job


class GenerationJob(Job):
    service: GenerationService
    manager: GenerationRequestManager

    @inject
    def __init__(
        self,
        service: GenerationService,
        manager: GenerationRequestManager
    ):
        self.service = service
        self.manager = manager

    def handle(self, id_: int):
        generation_request = self.manager.find_or_throw(id_)

        self.mark_started(generation_request)

        spec = GenerationSpec(**generation_request.spec)
        try:
            self.service.handle(spec)
            self.mark_completed(generation_request)
        except Exception as e:
            self.mark_failed(generation_request)
            raise e

    def mark_started(self, generation_request: GenerationRequest):
        generation_request.started = datetime.now()
        self.manager.save(generation_request)

    def mark_completed(self, generation_request: GenerationRequest):
        generation_request.completed = datetime.now()
        self.manager.save(generation_request)

    def mark_failed(self, generation_request: GenerationRequest):
        generation_request.failed = datetime.now()
        self.manager.save(generation_request)
