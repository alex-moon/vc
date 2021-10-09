from injector import inject

from vc.command.base import BaseCommand
from vc.service.inpainting import InpaintingService, InpaintingOptions


class InpaintingCommand(BaseCommand):
    inpainting: InpaintingService

    @inject
    def __init__(self, inpainting: InpaintingService):
        self.inpainting = inpainting

    def handle(self, args):
        self.inpainting.handle(InpaintingOptions(
            input_file='output.png',
            output_filename='debug.png',
            crop_border=[0., 0., 0., 0.],
            dynamic_fov=True
        ))
