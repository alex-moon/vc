import os
from datetime import datetime
from subprocess import Popen, PIPE
import numpy as np
from PIL import Image
from injector import inject
from tqdm import tqdm

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
        last_frame,
        output_file=OUTPUT_FILENAME,
        steps_dir=STEPS_DIR
    ):
        init_frame = 1

        min_fps = 10
        max_fps = 60

        total_frames = last_frame - init_frame

        length = 15  # in seconds

        frames = []
        tqdm.write('Generating video...')
        for step in range(init_frame, last_frame):
            path = os.path.join(steps_dir, f'{step:04}.png')
            print('appending frame', path)
            frames.append(Image.open(path))

        # fps = last_frame/10
        fps = np.clip(total_frames / length, min_fps, max_fps)

        p = Popen([
            'ffmpeg',
            '-y',
            '-f', 'image2pipe',
            '-vcodec', 'png',
            '-r', str(fps),
            '-i',
            '-',
            '-vcodec', 'libx264',
            '-r', str(fps),
            '-pix_fmt', 'yuv420p',
            '-crf', '17',
            '-preset', 'veryslow',
            output_file
        ], stdin=PIPE)
        for im in tqdm(frames):
            im.save(p.stdin, 'PNG')
        p.stdin.close()
        p.wait()

        now = datetime.now()
        self.file_service.put(output_file, '%s-%s' % (
            now.strftime('%Y-%m-%d-%H-%M-%S'),
            output_file
        ))

