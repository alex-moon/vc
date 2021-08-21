import json
from typing import Union
from injector import inject
from os.path import isfile
from shutil import copy

from vc.service import VqganClipService, InpaintingService, VideoService
from vc.service.vqgan_clip import VqganClipOptions
from vc.service.inpainting import InpaintingOptions
from vc.value_object import GenerationSpec, ImageSpec, VideoSpec


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
        if spec.images:
            for image in spec.images:
                if image.texts:
                    for text in image.texts:
                        if image.styles:
                            for style in image.styles:
                                for i in range(image.epochs):
                                    self.generate_image(image, '%s | %s' % (
                                        text,
                                        style
                                    ))
                        else:
                            for i in range(image.epochs):
                                self.generate_image(image, text)

        step = 0
        if spec.videos:
            for video in spec.videos:
                if video.texts:
                    for text in video.texts:
                        if video.styles:
                            for style in video.styles:
                                for i in range(video.epochs):
                                    self.generate_image(video, '%s | %s' % (
                                        text,
                                        style
                                    ))
                                    copy(self.OUTPUT_FILENAME, f'steps/{step:04}.png')
                                    step += 1
                        else:
                            for i in range(video.epochs):
                                self.generate_image(video, text)
                                copy(self.OUTPUT_FILENAME, f'steps/{step:04}.png')
                                step += 1

            self.video.make_video(step, json.dumps(spec, indent=4))
        print('done')

    def generate_image(self, spec: Union[ImageSpec, VideoSpec], prompt: str):
        self.vqgan_clip.handle(VqganClipOptions(**{
            'prompts': prompt,
            'max_iterations': spec.iterations,
            'init_image': (
                self.OUTPUT_FILENAME
                if isfile(self.OUTPUT_FILENAME)
                else None
            ),
        }))
        self.inpainting.handle(InpaintingOptions(**{
            'x_shift_range': [spec.x_shift],
            'y_shift_range': [spec.y_shift],
            'z_shift_range': [spec.z_shift],
        }))
