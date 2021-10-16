import os
import random
import string
from datetime import datetime

from injector import inject

from vc.service import FileService


class VideoService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.mp4'
    MINTERPOLATE_CONFIG = {
        'mi_mode': 'mci',
        'mc_mode': 'aobmc',
        'me_mode': 'bidir',
        'vsbmc': '1',
        'fps': '60',
    }
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def make_unwatermarked_video(
        self,
        output_file=OUTPUT_FILENAME,
        steps_dir=STEPS_DIR,
        now: datetime = None,
        suffix: str = None,
        interpolate: bool = False
    ):
        if suffix is None:
            suffix = self.generate_suffix()
        output_file = output_file.replace('.mp4', '-%s.mp4' % suffix)

        # @todo might be worth breaking this into a couple of steps for clarity
        minterpolate_string = '-filter:v "minterpolate=\'%s\'"' % ':'.join([
            '='.join([key, value])
            for key, value
            in self.MINTERPOLATE_CONFIG.items()
        ]) if interpolate else ''

        os.system(' '.join([
            'ffmpeg -y -i "%s/%%04d.png"' % steps_dir,
            '-b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2',
            minterpolate_string,
            output_file
        ]))

        return self.file_service.put(output_file, output_file, now)

    def make_watermarked_video(
        self,
        upscaled,
        output_file=OUTPUT_FILENAME,
        steps_dir=STEPS_DIR,
        now: datetime = None
    ):
        suffix = 'watermarked'
        output_file = output_file.replace('.mp4', '-%s.mp4' % suffix)
        watermark_file = (
            'app/assets/watermark.png'
            if upscaled
            else 'app/assets/watermark-400.png'
        )
        os.system(' '.join([
            'ffmpeg -y -i "%s/%%04d.png"' % steps_dir,
            '-i %s -filter_complex "overlay=0:0"' % watermark_file,
            '-b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2',
            output_file
        ]))

        return self.file_service.put(output_file, output_file, now)

    def generate_suffix(self):
        return ''.join(
            random.sample(
                string.ascii_lowercase + string.ascii_uppercase,
                k=16
            )
        )
