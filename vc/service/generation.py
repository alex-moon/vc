import json
import os
from time import time
from dataclasses import asdict
from injector import inject
from shutil import copy

from vc.service import VqganClipService, InpaintingService, VideoService
from vc.service.vqgan_clip import VqganClipOptions
from vc.service.inpainting import InpaintingOptions
from vc.value_object import GenerationSpec, ImageSpec


class GenerationService:
    OUTPUT_FILENAME = 'output.png'
    ACCELERATION = 0.01

    vqgan_clip: VqganClipService
    inpainting: InpaintingService
    video: VideoService

    hpy = None

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
        start = time()

        x_velocity = 0.
        y_velocity = 0.
        z_velocity = 0.

        def generate_image(
            spec: ImageSpec,
            prompt: str
        ):
            nonlocal x_velocity
            nonlocal y_velocity
            nonlocal z_velocity

            # accelerate toward intended velocity @todo cleaner way to do this
            if x_velocity > spec.x_shift:
                x_velocity -= self.ACCELERATION
            if x_velocity < spec.x_shift:
                x_velocity += self.ACCELERATION
            if y_velocity > spec.y_shift:
                y_velocity -= self.ACCELERATION
            if y_velocity < spec.y_shift:
                y_velocity += self.ACCELERATION
            if z_velocity > spec.z_shift:
                z_velocity -= self.ACCELERATION
            if z_velocity < spec.z_shift:
                z_velocity += self.ACCELERATION

            self.vqgan_clip.handle(VqganClipOptions(**{
                'prompts': prompt,
                'max_iterations': spec.iterations,
                'init_image': (
                    self.OUTPUT_FILENAME
                    if os.path.isfile(self.OUTPUT_FILENAME)
                    else None
                ),
            }))

            self.inpainting.handle(InpaintingOptions(**{
                'x_shift': x_velocity,
                'y_shift': y_velocity,
                'z_shift': z_velocity,
            }))

        if spec.images:
            for image in spec.images:
                if image.texts:
                    for text in image.texts:
                        if image.styles:
                            for style in image.styles:
                                for i in range(image.epochs):
                                    generate_image(
                                        image,
                                        '%s | %s' % (text, style)
                                    )
                        else:
                            for i in range(image.epochs):
                                generate_image(image, text)

        step = 0
        if spec.videos:
            for video in spec.videos:
                if video.steps:
                    for video_step in video.steps:
                        if video_step.texts:
                            for text in video_step.texts:
                                if video_step.styles:
                                    for style in video_step.styles:
                                        for i in range(video_step.epochs):
                                            generate_image(
                                                video_step,
                                                '%s | %s' % (text, style)
                                            )
                                            copy(self.OUTPUT_FILENAME, f'steps/{step:04}.png')
                                            step += 1
                                else:
                                    for i in range(video_step.epochs):
                                        generate_image(video_step, text)
                                        copy(self.OUTPUT_FILENAME, f'steps/{step:04}.png')
                                        step += 1

            self.video.make_video(step, json.dumps(asdict(spec), indent=4))

        end = time()
        print('done in %s seconds', end - start)
