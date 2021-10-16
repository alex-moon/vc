from injector import inject

from vc.event import (
    GenerationRequestCreatedEvent,
    GenerationRequestCancelledEvent,
)
from vc.event_listener.base import VcEventListener
from vc.job.generation import GenerationJob
from vc.service.job import JobService


class GenerationRequestCreatedEventListener(VcEventListener):
    job_service: JobService

    @inject
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def on(self, event: GenerationRequestCreatedEvent):
        event.generation_request.hash = self.job_service.enqueue(
            GenerationJob,
            event.generation_request.id
        )


class GenerationRequestCancelledEventListener(VcEventListener):
    job_service: JobService

    @inject
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def on(self, event: GenerationRequestCancelledEvent):
        self.job_service.cancel(event.generation_request.hash)
