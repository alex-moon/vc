from datetime import datetime

from dacite import from_dict
from injector import inject

from vc.job.base import Job
from vc.manager.generation_request import GenerationRequestManager
from vc.manager.generation_result import GenerationResultManager
from vc.model.generation_request import GenerationRequest
from vc.service.generation import GenerationService
from vc.value_object import GenerationSpec
from vc.value_object.generation_progress import GenerationProgress


class GenerationJob(Job):
    service: GenerationService
    request_manager: GenerationRequestManager
    result_manager: GenerationResultManager

    @inject
    def __init__(
        self,
        service: GenerationService,
        request_manager: GenerationRequestManager,
        result_manager: GenerationResultManager
    ):
        self.service = service
        self.request_manager = request_manager
        self.result_manager = result_manager

    def handle(self, id_: int):
        generation_request = self.request_manager.find_or_throw(id_)

        self.mark_started(generation_request)

        spec = from_dict(
            data_class=GenerationSpec,
            data=generation_request.spec
        )

        def update_progress(generation_progress: GenerationProgress):
            self.update_progress(generation_request, generation_progress)

        steps_completed = generation_request.steps_completed or 0
        name = generation_request.name
        try:
            self.service.handle(spec, update_progress, steps_completed, name)
            self.mark_completed(generation_request)
        except Exception as e:
            self.mark_failed(generation_request)
            raise e

    def mark_started(self, generation_request: GenerationRequest):
        if not generation_request.started:
            generation_request.started = datetime.now()
            self.request_manager.save(generation_request)

    def mark_completed(self, generation_request: GenerationRequest):
        generation_request.completed = datetime.now()
        self.request_manager.save(generation_request)

    def mark_failed(self, generation_request: GenerationRequest):
        generation_request.failed = datetime.now()
        generation_request.retried = None
        self.request_manager.save(generation_request)

    def update_progress(
        self,
        generation_request: GenerationRequest,
        generation_progress: GenerationProgress
    ):
        generation_request.steps_total = generation_progress.steps_total
        generation_request.steps_completed = generation_progress.steps_completed

        if generation_progress.name:
            generation_request.name = generation_progress.name

        if generation_progress.preview:
            generation_request.preview = generation_progress.preview

        if generation_progress.interim:
            generation_request.interim = generation_progress.interim

        if generation_progress.interim_watermarked:
            generation_request.interim_watermarked = generation_progress.interim_watermarked

        if generation_progress.result or generation_progress.result_watermarked:
            self.result_manager.create({
                'request_id': generation_request.id,
                'url': generation_progress.result,
                'url_watermarked': generation_progress.result_watermarked,
            })

        self.request_manager.save(generation_request)
