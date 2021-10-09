from injector import inject

from vc.command.base import BaseCommand
from vc.service.inpainting import InpaintingService, InpaintingOptions


class InpaintingCommand(BaseCommand):
    description = 'Runs inpainting on an input file'
    args = [
        {
            'dest': 'input_file',
            'type': str,
            'help': 'Input file',
            'default': 'output.png',
        },
        {
            'dest': 'output_file',
            'type': str,
            'help': 'Output file',
            'default': 'debug.png',
        },
    ]

    inpainting: InpaintingService

    @inject
    def __init__(self, inpainting: InpaintingService):
        self.inpainting = inpainting

    def handle(self, args):
        self.inpainting.handle(InpaintingOptions(
            input_file=args.input_file,
            output_filename=args.output_file
        ))
