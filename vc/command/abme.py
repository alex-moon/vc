from injector import inject

from vc.command.base import BaseCommand
from vc.service.abme import AbmeService, AbmeOptions


class AbmeCommand(BaseCommand):
    description = 'Runs abme on an input file'
    args = [
        {
            'dest': 'first_file',
            'type': str,
            'help': 'First file',
            'default': 'first.png',
            'nargs': '?',
        },
        {
            'dest': 'second_file',
            'type': str,
            'help': 'Second file',
            'default': 'second.png',
            'nargs': '?',
        },
        {
            'dest': 'output_file',
            'type': str,
            'help': 'Output file',
            'default': 'debug.png',
            'nargs': '?',
        },
    ]

    abme: AbmeService

    @inject
    def __init__(self, abme: AbmeService):
        self.abme = abme

    def handle(self, args):
        print('got %s %s %s' % (args.first_file, args.second_file, args.output_file))
        self.abme.handle(AbmeOptions(
            first_file=args.first_file,
            second_file=args.second_file,
            output_file=args.output_file,
        ))
