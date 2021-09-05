import json
import os
from dataclasses import asdict
from datetime import timedelta
from shutil import copy
from time import time

from injector import inject

from vc.service import VqganClipService, InpaintingService, VideoService
from vc.service.helper import DiagnosisHelper as dh
from vc.service.inpainting import InpaintingOptions
from vc.service.vqgan_clip import VqganClipOptions
from vc.value_object import GenerationSpec, ImageSpec


class GenerationService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.png'
    ACCELERATION = 0.01
    TRANSITION_SPEED = 0.0005
    VELOCITY_MULTIPLIER = -0.0001
    INTERIM_STEPS = 5

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

        last_text = None
        text_transition = 0.
        last_style = None
        style_transition = 0.

        def generate_image(
            spec: ImageSpec,
            text: str,
            style: str = None
        ):
            nonlocal x_velocity
            nonlocal y_velocity
            nonlocal z_velocity
            nonlocal last_text
            nonlocal text_transition
            nonlocal last_style
            nonlocal style_transition

            # accelerate toward intended velocity @todo cleaner way to do this
            if x_velocity > spec.x_velocity:
                x_velocity -= self.ACCELERATION
            if x_velocity < spec.x_velocity:
                x_velocity += self.ACCELERATION
            if y_velocity > spec.y_velocity:
                y_velocity -= self.ACCELERATION
            if y_velocity < spec.y_velocity:
                y_velocity += self.ACCELERATION
            if z_velocity > spec.z_velocity:
                z_velocity -= self.ACCELERATION
            if z_velocity < spec.z_velocity:
                z_velocity += self.ACCELERATION

            if last_text is None:
                last_text = text

            if last_style is None:
                last_style = style

            prompt = text
            if text != last_text:
                if text_transition < 1.:
                    prompt = '%s : %s | %s : %s' % (
                        last_text,
                        1. - text_transition,
                        text,
                        text_transition
                    )
                    text_transition += self.TRANSITION_SPEED
                else:
                    last_text = text
                    text_transition = 0.

            if style is not None:
                styles = style

                if style != last_style:
                    if style_transition < 1.:
                        styles = '%s : %s | %s : %s' % (
                            last_style,
                            1. - style_transition,
                            style,
                            style_transition
                        )
                        style_transition += self.TRANSITION_SPEED
                    else:
                        last_style = style
                        style_transition = 0.

                prompt = '%s | %s' % (prompt, styles)

            x_shift = x_velocity * self.VELOCITY_MULTIPLIER
            y_shift = y_velocity * self.VELOCITY_MULTIPLIER
            z_shift = z_velocity * self.VELOCITY_MULTIPLIER

            dh.debug('prompt', prompt)
            dh.debug('x_velocity', x_velocity)
            dh.debug('y_velocity', y_velocity)
            dh.debug('z_velocity', z_velocity)
            dh.debug('x_shift', x_shift)
            dh.debug('y_shift', y_shift)
            dh.debug('z_shift', z_shift)

            self.vqgan_clip.handle(VqganClipOptions(**{
                'prompts': prompt,
                'max_iterations': spec.iterations,
                'init_image': (
                    self.OUTPUT_FILENAME
                    if os.path.isfile(self.OUTPUT_FILENAME)
                    else None
                ),
                'output_filename': self.OUTPUT_FILENAME,
            }))

            if x_velocity != 0. or y_velocity != 0. or z_velocity != 0.:
                self.inpainting.handle(InpaintingOptions(**{
                    'input_file': self.OUTPUT_FILENAME,
                    'x_shift': x_shift,
                    'y_shift': y_shift,
                    'z_shift': z_shift,
                    'output_filename': self.OUTPUT_FILENAME,
                }))

        if spec.images:
            for image in spec.images:
                self.clean_files()
                if image.texts:
                    for text in image.texts:
                        if image.styles:
                            for style in image.styles:
                                for i in range(image.epochs):
                                    generate_image(image, text, style)
                        else:
                            for i in range(image.epochs):
                                generate_image(image, text)

        if spec.videos:
            for video in spec.videos:
                steps = self.calculate_total_steps(video)
                step = 0
                self.clean_files()
                if video.steps:
                    for video_step in video.steps:
                        if video_step.texts:
                            for text in video_step.texts:
                                if video_step.styles:
                                    for style in video_step.styles:
                                        for i in range(video_step.epochs):
                                            generate_image(
                                                video_step,
                                                text,
                                                style
                                            )
                                            copy(
                                                self.OUTPUT_FILENAME,
                                                f'steps/{step:04}.png'
                                            )
                                            step += 1
                                            self.handle_interim(
                                                step,
                                                steps,
                                                time() - start
                                            )
                                else:
                                    for i in range(video_step.epochs):
                                        generate_image(video_step, text)
                                        copy(
                                            self.OUTPUT_FILENAME,
                                            f'steps/{step:04}.png'
                                        )
                                        step += 1
                                        self.handle_interim(
                                            step,
                                            steps,
                                            time() - start
                                        )

                self.video.make_video(
                    step,
                    output_file=self.OUTPUT_FILENAME.replace('png', 'mp4'),
                    steps_dir=self.STEPS_DIR
                )

        print('done in %s', timedelta(seconds=time() - start))

    def handle_interim(self, step, steps, seconds):
        dh.debug('Completed %s of %s steps (%s%%) in %s' % (
            step,
            steps,
            round(step / steps * 100, 2),
            timedelta(seconds=seconds)
        ))

        if step % self.INTERIM_STEPS == 0:
            self.make_interim_video(step)

    def make_interim_video(self, step):
        output_file = self.OUTPUT_FILENAME.replace('.png', '-interim.mp4')
        dh.debug('making interim video', output_file)
        self.video.make_video(step, output_file, self.STEPS_DIR)

    def calculate_total_steps(self, video):
        step = 0
        for video_step in video.steps:
            if video_step.texts:
                for _ in video_step.texts:
                    if video_step.styles:
                        for _ in video_step.styles:
                            for i in range(video_step.epochs):
                                step += 1
                    else:
                        for i in range(video_step.epochs):
                            step += 1
        return step

    def clean_files(self):
        if os.path.exists(self.OUTPUT_FILENAME):
            os.remove(self.OUTPUT_FILENAME)
        for filename in os.listdir(self.STEPS_DIR):
            filepath = os.path.join(self.STEPS_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
