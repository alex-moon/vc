import json

from injector import inject
from os.path import isfile
from shutil import copy

from vc.service import VqganClipService, InpaintingService, VideoService
from vc.service.vqgan_clip import VqganClipOptions
from vc.service.inpainting import InpaintingOptions
from vc.value_object import GenerationSpec


class GenerationService:
    OUTPUT_FILENAME = 'output.png'

    vqgan_clip: VqganClipService
    inpainting: InpaintingService
    video: VideoService

    @inject
    def __init__(
        self,
        vqgan_clip: VqganClipService,
        inpainting: InpaintingService,
        video: VideoService
    ):
        self.vqgan_clip = vqgan_clip
        self.inpainting = inpainting
        self.video = video

    def handle(self, spec: GenerationSpec):
        print('starting')
        for image in spec.images:
            for text in image.texts:
                for style in image.styles:
                    for i in range(image.epochs):
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

        step = 0
        for video in spec.videos:
            for text in video.texts:
                for style in video.styles:
                    for i in range(video.epochs):
                        self.vqgan_clip.handle(VqganClipOptions(**{
                            'prompts': '%s | %s' % (text, style),
                            'max_iterations': video.iterations,
                            'init_image': (
                                self.OUTPUT_FILENAME
                                if isfile(self.OUTPUT_FILENAME)
                                else None
                            ),
                        }))
                        self.inpainting.handle(InpaintingOptions(**{
                            'x_shift_range': [video.x_shift],
                            'y_shift_range': [video.y_shift],
                            'z_shift_range': [video.z_shift],
                        }))
                        copy(self.OUTPUT_FILENAME, f'steps/{step:04}.png')
                        step += 1

            self.video.make_video(step, json.dumps(spec, indent=4))
        print('done')
