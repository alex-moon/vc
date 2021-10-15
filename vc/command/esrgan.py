from math import pi
from injector import inject

from vc.command.base import BaseCommand
from vc.service.esrgan import EsrganService, EsrganOptions


class EsrganCommand(BaseCommand):
    description = 'Runs esrgan on an input file'
    args = [
        {
            'dest': 'input_file',
            'type': str,
            'help': 'Input file',
            'default': 'output.png',
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

    esrgan: EsrganService

    @inject
    def __init__(self, esrgan: EsrganService):
        self.esrgan = esrgan

    def handle(self, args):
        print('got %s %s' % (args.input_file, args.output_file))
        self.esrgan.handle(EsrganOptions(
            input_file=args.input_file,
            output_file=args.output_file,
        ))
