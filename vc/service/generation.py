from datetime import timedelta
from time import time
from typing import Callable

from injector import inject

from vc.service.helper.steps import Steps
from vc.service.vqgan_clip import VqganClipService
from vc.service.inpainting import InpaintingService
from vc.service.esrgan import EsrganService
from vc.service.rife import RifeService
from vc.service.video import VideoService
from vc.service.file import FileService

from vc.service.helper import DiagnosisHelper as dh
from vc.service.helper.runner import GenerationRunner
from vc.value_object import GenerationSpec
from vc.value_object.generation_progress import GenerationProgress


class GenerationService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.png'

    vqgan_clip: VqganClipService
    inpainting: InpaintingService
    esrgan: EsrganService
    rife: RifeService
    video: VideoService
    file: FileService

    hpy = None

    @inject
    def __init__(
        self,
        vqgan_clip: VqganClipService,
        inpainting: InpaintingService,
        esrgan: EsrganService,
        rife: RifeService,
        video: VideoService,
        file: FileService
    ):
        self.vqgan_clip = vqgan_clip
        self.inpainting = inpainting
        self.esrgan = esrgan
        self.rife = rife
        self.video = video
        self.file = file

    def handle(
        self,
        spec: GenerationSpec,
        callback: Callable,
        steps_completed=0,
        name=None
    ):
        dh.debug('GenerationService', 'starting')
        start = time()

        steps_total = Steps.total_steps(spec)

        runner = GenerationRunner(
            self.vqgan_clip,
            self.inpainting,
            self.esrgan,
            self.rife,
            self.video,
            self.file,
            self.OUTPUT_FILENAME,
            self.STEPS_DIR,
            name=name
        )

        for step in Steps.iterate_steps(spec):
            if step.step <= steps_completed:
                continue

            steps_completed = step.step
            result = runner.handle(step)
            callback(GenerationProgress(
                steps_completed=steps_completed,
                steps_total=steps_total,
                name=runner.generation_name,
                preview=result.preview,
                result=result.result,
                result_watermarked=result.result_watermarked,
                interim=result.interim,
                interim_watermarked=result.interim_watermarked
            ))
            dh.debug('Completed %s of %s steps (%s%%) for %s in %s' % (
                steps_completed,
                steps_total,
                round(steps_completed / steps_total * 100, 2),
                runner.generation_name,
                timedelta(seconds=time() - start)
            ))

        dh.debug('GenerationService', 'done in', timedelta(seconds=time() - start))
