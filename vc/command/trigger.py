from injector import inject

from vc.command.base import BaseCommand
from vc.manager import GenerationRequestManager


class TriggerCommand(BaseCommand):
    description = 'Sends a job to the generation queue'
    args = [
        {
            'dest': 'id',
            'type': int,
            'help': 'Request id',
        }
    ]

    manager: GenerationRequestManager

    @inject
    def __init__(self, manager: GenerationRequestManager):
        self.manager = manager

    def handle(self, args):
        print('Triggering %s' % args.id)
        self.manager.trigger(args.id)
