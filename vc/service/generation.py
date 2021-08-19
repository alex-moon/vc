from injector import inject

from vc.service.vqgan_clip import VqganClipService
from vc.value_object import GenerationSpec


class GenerationService:
    vqgan_clip: VqganClipService

    @inject
    def __init__(self, vqgan_clip: VqganClipService):
        self.vqgan_clip = vqgan_clip

    def handle(self, spec: GenerationSpec):
        print('starting')
        self.vqgan_clip.handle(spec.images[0])
        print('done')
