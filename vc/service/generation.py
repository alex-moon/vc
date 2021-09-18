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
from vc.service.helper.runner import GenerationRunner
from vc.service.isr import IsrService
from vc.value_object import GenerationSpec
from vc.value_object.generation_progress import GenerationProgress


class GenerationService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.png'

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

        for step in GenerationRunner.iterate_steps(spec):
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
        for _ in GenerationRunner.iterate_steps(spec):
            steps_total += 1
        return steps_total
