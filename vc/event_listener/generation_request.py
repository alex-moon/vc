from injector import inject

from vc.job.categories import CategoriesJob
from vc.job.sentiment import SentimentJob
from vc.job.keywords import KeywordsJob
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
            CategoriesJob,
            event.generation_request.id
        )
        self.job_service.enqueue(
            SentimentJob,
            event.generation_request.id
        )
        self.job_service.enqueue(
            KeywordsJob,
            event.generation_request.id
        )
