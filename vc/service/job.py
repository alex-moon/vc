from typing import Type
from injector import inject

from vc.job import Job
from vc.service.queue import QueueService


class JobService:
    queue_service: QueueService

    @inject
    def __init__(self, queue_service: QueueService):
        self.queue_service = queue_service

    def enqueue(self, job: Type[Job], *args):
        self.queue_service.enqueue(job.handle, args=args)