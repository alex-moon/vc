from dacite import from_dict
from datetime import datetime
from injector import inject

from vc.value_object import GenerationSpec
from vc.manager.generation_request import GenerationRequestManager
from vc.model.generation_request import GenerationRequest
from vc.service.generation import GenerationService
from vc.job.base import Job
from vc.value_object.generation_progress import GenerationProgress


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

        spec = from_dict(
            data_class=GenerationSpec,
            data=generation_request.spec
        )

        def update_progress(generation_progress: GenerationProgress):
            self.update_progress(generation_request, generation_progress)

        try:
            self.service.handle(spec, update_progress)
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

    def update_progress(
        self,
        generation_request: GenerationRequest,
        generation_progress: GenerationProgress
    ):
        generation_request.steps_total = generation_progress.steps_total
        generation_request.steps_completed = generation_progress.steps_completed
        # @todo add results - generation_progress.result - need to push to list
        self.manager.save(generation_request)
