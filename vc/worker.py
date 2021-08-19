from vc.service.queue import QueueService

from . import create_app
from .injector import injector

if __name__ == '__main__':
    app = create_app()
    queue_service = injector.get(QueueService)
    queue_service.get_worker().work()
