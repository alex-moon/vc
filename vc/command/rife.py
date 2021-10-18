from injector import inject

from vc.command.base import BaseCommand
from vc.service.rife import RifeService, RifeOptions


class RifeCommand(BaseCommand):
    description = 'Runs rife on an input file'
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

    rife: RifeService

    @inject
    def __init__(self, rife: RifeService):
        self.rife = rife

    def handle(self, args):
        print('got %s %s %s' % (args.first_file, args.second_file, args.output_file))
        self.rife.handle(RifeOptions(
            first_file=args.first_file,
            second_file=args.second_file,
            output_file=args.output_file,
        ))
