import os
from datetime import datetime

from injector import inject

from vc.service import FileService


class VideoService:
    STEPS_DIR = 'steps'
    OUTPUT_FILENAME = 'output.mp4'
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def make_video(
        self,
        output_file=OUTPUT_FILENAME,
        steps_dir=STEPS_DIR,
        now: datetime = None
    ):
        os.system(' '.join([
            'ffmpeg -y -i "%s/%%04d.png"' % steps_dir,
            '-b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2',
            '-filter:v "minterpolate=\'mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60\'"',
            output_file
        ]))

        return self.file_service.put(output_file, output_file, now)
