from injector import inject
from os.path import isfile

from vc.service import VqganClipService, InpaintingService
from vc.service.vqgan_clip import VqganClipOptions
from vc.service.inpainting import InpaintingOptions
from vc.value_object import GenerationSpec


class GenerationService:
    OUTPUT_FILENAME = 'output.png'

    vqgan_clip: VqganClipService
    inpainting: InpaintingService

    @inject
    def __init__(
        self,
        vqgan_clip: VqganClipService,
        inpainting: InpaintingService
    ):
        self.vqgan_clip = vqgan_clip
        self.inpainting = inpainting

    def handle(self, spec: GenerationSpec):
        # @todo for each image, for each video, convert from ImageSpec
        # and VideoSpec to VqganClipOptions - hide the config (or make it
        # available under an "advanced" key or whatever)
        print('starting')
        for image in spec.images:
            for text in image.texts:
                for style in image.styles:
                    self.vqgan_clip.handle(VqganClipOptions(**{
                        'prompts': '%s | %s' % (text, style),
                        'max_iterations': image.iterations,
                        'init_image': (
                            self.OUTPUT_FILENAME
                            if isfile(self.OUTPUT_FILENAME)
                            else None
                        ),
                    }))
                    self.inpainting.handle(InpaintingOptions(**{
                        'x_shift_range': [image.x_shift],
                        'y_shift_range': [image.y_shift],
                        'z_shift_range': [image.z_shift],
                    }))
        print('done')
