from math import pi
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

    inpainting: InpaintingService

    @inject
    def __init__(self, inpainting: InpaintingService):
        self.inpainting = inpainting

    def handle(self, args):
        print('got %s %s' % (args.input_file, args.output_file))
        self.inpainting.handle(InpaintingOptions(
            input_file=args.input_file,
            output_filename=args.output_file,
            offscreen_rendering=True,
            x_shift=-0.01,
            y_shift=0.01,
            z_shift=-0.01,
            pan=-(2 * pi / 360),
            tilt=-(2 * pi / 360),
            roll=-(2 * pi / 360)
        ))
