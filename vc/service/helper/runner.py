import os
from dataclasses import dataclass
from datetime import datetime
from shutil import copy
from math import log2

from vc.service import (
    VqganClipService,
    InpaintingService,
    VideoService,
    FileService,
)
from vc.service.helper import DiagnosisHelper as dh
from vc.service.helper.acceleration import Translate
from vc.service.helper.rotation import Rotate
from vc.service.inpainting import InpaintingOptions
from vc.service.esrgan import EsrganService, EsrganOptions
from vc.service.rife import RifeService, RifeOptions
from vc.service.helper.random_word import RandomWord
from vc.service.vqgan_clip import VqganClipOptions
from vc.value_object import ImageSpec, VideoStepSpec, GenerationSpec


@dataclass
class GenerationStep:
    step: int


@dataclass
class ImageGenerationStep(GenerationStep):
    spec: ImageSpec
    text: str
    style: str = None
    video_step: int = None


@dataclass
class VideoGenerationStep(GenerationStep):
    upscaled: bool
    interpolated: bool


@dataclass
class HandleInterimStep(VideoGenerationStep):
    pass


@dataclass
class CleanFilesStep(GenerationStep):
    pass


@dataclass
class GenerationResult:
    preview: str = None
    interim: str = None
    interim_watermarked: str = None
    result: str = None
    result_watermarked: str = None


class GenerationRunner:
    INTERIM_STEPS = 60
    TRANSITION_SPEED = 0.05
    INTERPOLATE_MULTIPLE = 4

    vqgan_clip: VqganClipService
    inpainting: InpaintingService
    esrgan: EsrganService
    rife: RifeService
    video: VideoService
    file: FileService

    output_filename: str
    steps_dir: str

    generation_name: str
    now: datetime
    suffix: str

    spec: ImageSpec = None
    translate: Translate = None
    rotate: Rotate = None

    last_text = None
    text_transition = 0.
    last_style = None
    style_transition = 0.

    def __init__(
        self,
        vqgan_clip: VqganClipService,
        inpainting: InpaintingService,
        esrgan: EsrganService,
        rife: RifeService,
        video: VideoService,
        file: FileService,
        output_filename: str,
        steps_dir: str,
        name: str = None
    ):
        self.vqgan_clip = vqgan_clip
        self.inpainting = inpainting
        self.esrgan = esrgan
        self.rife = rife
        self.video = video
        self.file = file
        self.output_filename = output_filename
        self.steps_dir = steps_dir
        self.generation_name = name if name else RandomWord.get()
        self.now = datetime.now()
        self.suffix = self.video.generate_suffix()

    def handle(self, step: GenerationStep) -> GenerationResult:
        if isinstance(step, ImageGenerationStep):
            dh.debug('GenerationRunner', 'generate_image', step)
            result = self.generate_image(step)

            if isinstance(step.spec, VideoStepSpec):
                return GenerationResult(
                    preview=result
                )

            return GenerationResult(
                result=result
            )

        if isinstance(step, HandleInterimStep):
            dh.debug('GenerationRunner', 'handle_interim', step)
            interim, interim_watermarked = self.handle_interim(step)
            return GenerationResult(
                interim=interim,
                interim_watermarked=interim_watermarked
            )

        if isinstance(step, VideoGenerationStep):
            dh.debug('GenerationRunner', 'make_video', step)
            result, result_watermarked = self.make_video(step)
            return GenerationResult(
                result=result,
                result_watermarked=result_watermarked
            )

        if isinstance(step, CleanFilesStep):
            dh.debug('GenerationRunner', 'clean_files', step)
            self.clean_files(step)
            return GenerationResult()

    def generate_image(self, step: ImageGenerationStep):
        if step.spec != self.spec:
            self.spec = step.spec
            if isinstance(self.spec, VideoStepSpec):
                self.translate = Translate(
                    self.spec.x_velocity,
                    self.spec.y_velocity,
                    self.spec.z_velocity,
                    previous=self.translate
                )
                self.rotate = Rotate(
                    self.spec.tilt_velocity,
                    self.spec.pan_velocity,
                    self.spec.roll_velocity,
                    previous=self.rotate
                )

        text = step.text
        style = step.style

        moving = False
        rotating = False
        x_shift, y_shift, z_shift = 0., 0., 0.
        pan, tilt, roll = 0., 0., 0.
        prompt = text if style is None else '%s | %s' % (text, style)

        if isinstance(self.spec, VideoStepSpec):
            if self.last_text is None:
                self.last_text = text

            if self.last_style is None:
                self.last_style = style

            # @todo VC-28: generalise this for any number of text lists
            prompt = text
            if text != self.last_text:
                if self.text_transition < 1.:
                    prompt = '%s : %s | %s : %s' % (
                        self.last_text,
                        1. - self.text_transition,
                        text,
                        self.text_transition
                    )
                    self.text_transition += self.TRANSITION_SPEED
                else:
                    self.last_text = text
                    self.text_transition = 0.

            if style is not None:
                styles = style

                if style != self.last_style:
                    if self.style_transition < 1.:
                        styles = '%s : %s | %s : %s' % (
                            self.last_style,
                            1. - self.style_transition,
                            style,
                            self.style_transition
                        )
                        self.style_transition += self.TRANSITION_SPEED
                    else:
                        self.last_style = style
                        self.style_transition = 0.

                prompt = '%s | %s' % (prompt, styles)

            moving = self.translate.move()
            rotating = self.rotate.rotate()
            x_shift, y_shift, z_shift = self.translate.velocity.to_tuple()
            tilt, pan, roll = self.rotate.velocity.to_tuple()

            dh.debug('GenerationRunner', 'prompt', prompt)
            dh.debug('GenerationRunner', 'x_shift', x_shift)
            dh.debug('GenerationRunner', 'y_shift', y_shift)
            dh.debug('GenerationRunner', 'z_shift', z_shift)
            dh.debug('GenerationRunner', 'tilt', tilt)
            dh.debug('GenerationRunner', 'pan', pan)
            dh.debug('GenerationRunner', 'roll', roll)

            if self.spec.init_iterations and not os.path.isfile(self.output_filename):
                dh.debug('GenerationRunner', 'init', self.spec.init_iterations)
                self.vqgan_clip.handle(VqganClipOptions(**{
                    'prompts': prompt,
                    'max_iterations': self.spec.init_iterations,
                    'output_filename': self.output_filename,
                    'init_image': None
                }))

        dh.debug('GenerationRunner', 'vqgan_clip', 'handle')
        self.vqgan_clip.handle(VqganClipOptions(**{
            'prompts': prompt,
            'max_iterations': self.spec.iterations,
            'init_image': (
                self.output_filename
                if os.path.isfile(self.output_filename)
                else None
            ),
            'output_filename': self.output_filename,
        }))

        if moving or rotating:
            dh.debug('GenerationRunner', 'inpainting', 'handle')
            self.inpainting.handle(InpaintingOptions(**{
                'input_file': self.output_filename,
                'x_shift': x_shift,
                'y_shift': y_shift,
                'z_shift': z_shift,
                'tilt': tilt,
                'pan': pan,
                'roll': roll,
                'output_filename': self.output_filename,
            }))
        else:
            dh.debug('GenerationRunner', 'inpainting', 'skipped (not moving)')

        filename_to_use = self.output_filename
        if self.spec.upscale:
            filename_to_use = filename_to_use.replace('.png', '-upscaled.png')
            dh.debug('GenerationRunner', 'esrgan', 'handle')
            self.esrgan.handle(EsrganOptions(**{
                'input_file': self.output_filename,
                'output_file': filename_to_use,
            }))

        if not step.video_step:
            return self.file.put(
                self.output_filename,
                '%s-%s.png' % (self.generation_name, step.step)
            )

        video_step = step.video_step
        if self.spec.interpolate:
            video_step = (video_step - 1) * self.INTERPOLATE_MULTIPLE + 1

        step_filepath = self.video_step_filepath(video_step)
        dh.debug('GenerationRunner', 'video_step', step_filepath)
        copy(filename_to_use, step_filepath)

        if self.spec.interpolate and video_step > 1:
            second_file = step_filepath
            step_from = video_step - self.INTERPOLATE_MULTIPLE
            first_file = self.video_step_filepath(step_from)
            self.rife.handle(RifeOptions(
                first_file=first_file,
                second_file=second_file,
                output_file=lambda i: self.video_step_filepath(i + step_from),
                exp=int(log2(self.INTERPOLATE_MULTIPLE))
            ))

        return self.file.put(
            self.output_filename,
            '%s-preview.png' % self.generation_name,
            self.now
        )

    def video_step_filepath(self, video_step):
        return os.path.join(self.steps_dir, f'{video_step:04}.png')

    def handle_interim(self, step: HandleInterimStep):
        return self.make_video(step)

    def make_video(self, step: VideoGenerationStep):
        is_interim = isinstance(step, HandleInterimStep)
        filename = '%s-%s.mp4' % (
            self.generation_name,
            'interim' if is_interim else 'result'
        )
        interpolate = not is_interim
        if isinstance(self.spec, VideoStepSpec):
            interpolate = interpolate and not step.interpolated
        unwatermarked = self.video.make_unwatermarked_video(
            output_file=filename,
            steps_dir=self.steps_dir,
            now=self.now if is_interim else None,
            suffix=self.suffix if is_interim else None,
            interpolate=interpolate,
            fps_multiple=self.INTERPOLATE_MULTIPLE if step.interpolated else 1
        )
        watermarked = self.video.make_watermarked_video(
            step.upscaled,
            output_file=filename,
            steps_dir=self.steps_dir,
            now=self.now if is_interim else None,
            fps_multiple=self.INTERPOLATE_MULTIPLE if step.interpolated else 1
        )
        return unwatermarked, watermarked

    def clean_files(self, step: CleanFilesStep):
        if os.path.exists(self.output_filename):
            os.remove(self.output_filename)
        for filename in os.listdir(self.steps_dir):
            filepath = os.path.join(self.steps_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        return None

    @classmethod
    def iterate_steps(cls, spec: GenerationSpec):
        step = 0

        if spec.images:
            for step_spec in spec.images:
                step += 1
                yield CleanFilesStep(step)

                if step_spec.texts:
                    for text in step_spec.texts:
                        if step_spec.styles:
                            for style in step_spec.styles:
                                step += 1
                                yield CleanFilesStep(step)
                                step += 1
                                yield ImageGenerationStep(
                                    spec=step_spec,
                                    step=step,
                                    text=text,
                                    style=style
                                )
                        else:
                            step += 1
                            yield CleanFilesStep(step)
                            step += 1
                            yield ImageGenerationStep(
                                spec=step_spec,
                                step=step,
                                text=text
                            )

        if spec.videos:
            for video in spec.videos:
                upscaled = False
                interpolated = False
                video_step = 0
                step += 1
                yield CleanFilesStep(step=step)
                if video.steps:
                    for step_spec in video.steps:
                        if step_spec.upscale:
                            upscaled = True
                        if step_spec.interpolate:
                            interpolated = True

                        if step_spec.texts:
                            for text in step_spec.texts:
                                if step_spec.styles:
                                    for style in step_spec.styles:
                                        for i in range(step_spec.epochs):
                                            video_step += 1
                                            step += 1
                                            yield ImageGenerationStep(
                                                spec=step_spec,
                                                step=step,
                                                text=text,
                                                style=style,
                                                video_step=video_step
                                            )

                                            if step % cls.INTERIM_STEPS == 1:
                                                step += 1
                                                yield HandleInterimStep(
                                                    step=step,
                                                    upscaled=upscaled,
                                                    interpolated=interpolated
                                                )
                                else:
                                    for i in range(step_spec.epochs):
                                        video_step += 1
                                        step += 1
                                        yield ImageGenerationStep(
                                            spec=step_spec,
                                            step=step,
                                            text=text,
                                            video_step=video_step
                                        )

                                        if step % cls.INTERIM_STEPS == 1:
                                            step += 1
                                            yield HandleInterimStep(
                                                step=step,
                                                upscaled=upscaled,
                                                interpolated=interpolated
                                            )

                step += 1
                yield VideoGenerationStep(
                    step=step,
                    upscaled=upscaled,
                    interpolated=interpolated
                )
