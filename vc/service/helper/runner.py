import os
from dataclasses import dataclass
from datetime import datetime
from math import log2
from shutil import copy

from vc.service.esrgan import EsrganService, EsrganOptions
from vc.service.file import FileService
from vc.service.helper import DiagnosisHelper as dh
from vc.service.helper.acceleration import Translate
from vc.service.helper.dimensions import DimensionsHelper
from vc.service.helper.random_word import RandomWord
from vc.service.helper.rotation import Rotate
from vc.service.helper.walk import Walk
from vc.service.inpainting import InpaintingService, InpaintingOptions
from vc.service.rife import RifeService, RifeOptions
from vc.service.video import VideoService
from vc.service.vqgan_clip import VqganClipService, VqganClipOptions
from vc.value_object import ImageSpec, VideoStepSpec
from vc.service.helper.steps import (
    GenerationStep,
    ImageGenerationStep,
    VideoGenerationStep,
    CleanFilesStep,
    HandleInterimStep,
)


@dataclass
class GenerationResult:
    preview: str = None
    interim: str = None
    interim_watermarked: str = None
    result: str = None
    result_watermarked: str = None


class GenerationRunner:
    MESH_DIR = 'mesh'
    DEPTH_DIR = 'depth'
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
            if isinstance(step.spec, VideoStepSpec):
                self.translate = Translate(
                    step.spec.x_velocity,
                    step.spec.y_velocity,
                    step.spec.z_velocity,
                    previous=self.translate,
                    transition=step.spec.transition
                )
                self.rotate = Rotate(
                    step.spec.tilt_velocity,
                    step.spec.pan_velocity,
                    step.spec.roll_velocity,
                    previous=self.rotate,
                    transition=step.spec.transition
                )

        if isinstance(step.spec, VideoStepSpec) and step.spec.random_walk:
            self.translate = Translate(
                Walk.target().x,
                Walk.target().y,
                Walk.target().z,
                previous=self.translate,
                transition=2
            )
            self.rotate = Rotate(
                step.spec.tilt_velocity,
                Walk.target().pan,
                step.spec.roll_velocity,
                previous=self.rotate,
                transition=2
            )

        text = step.text
        style = step.style

        moving = False
        rotating = False
        x_shift, y_shift, z_shift = 0., 0., 0.
        pan, tilt, roll = 0., 0., 0.
        prompt = text if style is None else '%s | %s' % (text, style)

        reset = True
        if isinstance(step.spec, VideoStepSpec):
            if self.last_text is None:
                self.last_text = text

            if self.last_style is None:
                self.last_style = style

            transition_speed = 1. / step.spec.transition

            # @todo VC-28: generalise this for any number of text lists
            prompt = text
            if text != self.last_text:
                if self.text_transition < 1.:
                    self.text_transition += transition_speed
                    prompt = '%s : %s | %s : %s' % (
                        self.last_text,
                        1. - self.text_transition,
                        text,
                        self.text_transition
                    )
                else:
                    self.last_text = text
                    self.text_transition = 0.

            if style is not None:
                styles = style

                if style != self.last_style:
                    if self.style_transition < 1.:
                        self.style_transition += transition_speed
                        styles = '%s : %s | %s : %s' % (
                            self.last_style,
                            1. - self.style_transition,
                            style,
                            self.style_transition
                        )
                    else:
                        self.last_style = style
                        self.style_transition = 0.

                prompt = '%s | %s' % (prompt, styles)

            reset = (
                self.translate.should_reset()
                or self.rotate.should_reset()
                or True
            )
            if reset:
                self.translate.reset()
                self.rotate.reset()

            moving = self.translate.move()
            rotating = self.rotate.rotate()
            x_shift, y_shift, z_shift = self.translate.to_tuple()
            tilt, pan, roll = self.rotate.to_tuple()

            dh.debug('GenerationRunner', 'prompt', prompt)
            dh.debug('GenerationRunner', 'x_shift', x_shift)
            dh.debug('GenerationRunner', 'y_shift', y_shift)
            dh.debug('GenerationRunner', 'z_shift', z_shift)
            dh.debug('GenerationRunner', 'tilt', tilt)
            dh.debug('GenerationRunner', 'pan', pan)
            dh.debug('GenerationRunner', 'roll', roll)

            if step.spec.init_iterations and not os.path.isfile(self.output_filename):
                dh.debug('GenerationRunner', 'init', step.spec.init_iterations)
                self.vqgan_clip.handle(VqganClipOptions(
                    prompts=prompt,
                    max_iterations=step.spec.init_iterations,
                    output_filename=self.output_filename,
                    init_image=None
                ))

        if reset:
            dh.debug('GenerationRunner', 'vqgan_clip', 'handle')
            self.vqgan_clip.handle(VqganClipOptions(**{
                'prompts': prompt,
                'max_iterations': step.spec.iterations,
                'init_image': (
                    self.output_filename
                    if os.path.isfile(self.output_filename)
                    else None
                ),
                'output_filename': self.output_filename,
            }))

        if moving or rotating or reset:
            dh.debug('GenerationRunner', 'inpainting', 'handle')
            dh.debug('GenerationRunner', 'inpainting', 'load_ply', not reset)
            self.inpainting.handle(InpaintingOptions(
                input_file=self.output_filename,
                x_shift=x_shift,
                y_shift=y_shift,
                z_shift=z_shift,
                tilt=tilt,
                pan=pan,
                roll=roll,
                output_filename=self.output_filename,
                load_ply=not reset,
                mesh_folder=self.MESH_DIR,
                depth_folder=self.DEPTH_DIR
            ))
        else:
            dh.debug('GenerationRunner', 'inpainting', 'skipped (not moving)')

        filename_to_use = self.output_filename
        if step.spec.upscale:
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
        if step.spec.interpolate:
            video_step = (video_step - 1) * self.INTERPOLATE_MULTIPLE + 1

        step_filepath = self.video_step_filepath(video_step)
        dh.debug('GenerationRunner', 'video_step', step_filepath)
        copy(filename_to_use, step_filepath)

        if step.spec.interpolate and video_step > 1:
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
        interpolate = False and not step.interpolated
        width = (
            DimensionsHelper.width_large()
            if step.upscaled
            else DimensionsHelper.width_small()
        )
        unwatermarked = self.video.make_unwatermarked_video(
            output_file=filename,
            steps_dir=self.steps_dir,
            now=self.now if is_interim else None,
            suffix=self.suffix if is_interim else None,
            interpolate=interpolate,
            fps_multiple=self.INTERPOLATE_MULTIPLE if step.interpolated else 1
        )
        watermarked = self.video.make_watermarked_video(
            width=width,
            output_file=filename,
            steps_dir=self.steps_dir,
            now=self.now if is_interim else None,
            fps_multiple=self.INTERPOLATE_MULTIPLE if step.interpolated else 1
        )
        return unwatermarked, watermarked

    def clean_files(self, step: CleanFilesStep):
        if os.path.exists(self.output_filename):
            os.remove(self.output_filename)

        for filename in os.listdir(self.MESH_DIR):
            if filename[-4:] != '.ply':
                continue

            filepath = os.path.join(self.MESH_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for filename in os.listdir(self.DEPTH_DIR):
            if filename[-4:] != '.pfm' and filename[-4:] != 'png':
                continue

            filepath = os.path.join(self.DEPTH_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for filename in os.listdir(self.steps_dir):
            if filename[-4:] != '.png':
                continue

            filepath = os.path.join(self.steps_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        return None
