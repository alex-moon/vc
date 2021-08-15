from injector import inject

from vc.job.generation import GenerationJob
from vc.service.job import JobService
from vc.event import GenerationRequestCreatedEvent
from vc.event_listener.base import VcEventListener


class GenerationRequestCreatedEventListener(VcEventListener):
    job_service: JobService

    @inject
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def on(self, event: GenerationRequestCreatedEvent):
        self.job_service.enqueue(
            GenerationJob,
            event.generation_request.id
        )
