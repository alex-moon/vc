from injector import inject

from vc.service import VqganClipService, InpaintingService
from vc.value_object import GenerationSpec


class GenerationService:
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
            result = self.vqgan_clip.handle(image)
            # result = self.inpainting.handle(image)
        print('done')
