from datetime import timedelta
from time import time
from typing import Callable

from injector import inject

from vc.service import (
    VqganClipService,
    InpaintingService,
    VideoService,
    FileService,
)
from vc.service.helper import DiagnosisHelper as dh
from vc.service.helper.runner import (
    GenerationRunner,
    VideoGenerationStep,
    ImageGenerationStep,
    HandleInterimStep,
    CleanFilesStep,
)
from vc.service.isr import IsrService
from vc.value_object import GenerationSpec
from vc.value_object.generation_progress import GenerationProgress


class GenerationService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.png'
    INTERIM_STEPS = 20

    vqgan_clip: VqganClipService
    inpainting: InpaintingService
    isr: IsrService
    video: VideoService
    file: FileService

    hpy = None

    @inject
    def __init__(
        self,
        vqgan_clip: VqganClipService,
        inpainting: InpaintingService,
        isr: IsrService,
        video: VideoService,
        file: FileService
    ):
        self.vqgan_clip = vqgan_clip
        self.inpainting = inpainting
        self.isr = isr
        self.video = video
        self.file = file

    def handle(self, spec: GenerationSpec, callback: Callable):
        print('starting')
        start = time()

        steps_total = self.calculate_total_steps(spec)

        runner = GenerationRunner(
            self.vqgan_clip,
            self.inpainting,
            self.isr,
            self.video,
            self.file,
            self.OUTPUT_FILENAME,
            self.STEPS_DIR
        )

        for step in self.iterate_steps(spec):
            steps_completed = step.step
            result = runner.handle(step)
            callback(GenerationProgress(
                steps_completed=steps_completed,
                steps_total=steps_total,
                name=runner.generation_name,
                result=result.result,
                preview=result.preview,
                interim=result.interim
            ))
            dh.debug('Completed %s of %s steps (%s%%) for %s in %s' % (
                steps_completed,
                steps_total,
                round(steps_completed / steps_total * 100, 2),
                runner.generation_name,
                timedelta(seconds=time() - start)
            ))

        print('done in %s', timedelta(seconds=time() - start))

    def calculate_total_steps(self, spec):
        steps_total = 0
        for _ in self.iterate_steps(spec):
            steps_total += 1
        return steps_total

    def iterate_steps(self, spec):
        step = 0

        if spec.images:
            for step_spec in spec.images:
                step += 1
                yield CleanFilesStep(step)

                if step_spec.texts:
                    for text in step_spec.texts:
                        if step_spec.styles:
                            for style in step_spec.styles:
                                for i in range(step_spec.epochs):
                                    step += 1
                                    yield ImageGenerationStep(
                                        spec=step_spec,
                                        step=step,
                                        text=text,
                                        style=style
                                    )

                                    if step % self.INTERIM_STEPS == 0:
                                        step += 1
                                        yield HandleInterimStep(
                                            step=step
                                        )
                        else:
                            for i in range(step_spec.epochs):
                                step += 1
                                yield ImageGenerationStep(
                                    spec=step_spec,
                                    step=step,
                                    text=text
                                )

                                if step % self.INTERIM_STEPS == 0:
                                    step += 1
                                    yield HandleInterimStep(
                                        step=step
                                    )

        if spec.videos:
            for video in spec.videos:
                video_step = 0
                step += 1
                yield CleanFilesStep(step=step)
                if video.steps:
                    for step_spec in video.steps:
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

                                            if step % self.INTERIM_STEPS == 0:
                                                step += 1
                                                yield HandleInterimStep(
                                                    step=step
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

                                        if step % self.INTERIM_STEPS == 0:
                                            step += 1
                                            yield HandleInterimStep(
                                                step=step
                                            )

                step += 1
                yield VideoGenerationStep(step=step)
