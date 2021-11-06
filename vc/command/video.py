from injector import inject

from vc.command.base import BaseCommand
from vc.service import VideoService


class VideoCommand(BaseCommand):
    description = 'Makes a video from steps files'
    args = [
        {
            'dest': 'fps_multiple',
            'type': int,
            'help': 'FPS multiple (1 or 4)',
            'default': 4,
        },
        {
            'dest': 'steps_dir',
            'type': str,
            'help': 'Steps dir',
            'default': 'steps',
            'nargs': '?',
        }
    ]

    video: VideoService

    @inject
    def __init__(self, video: VideoService):
        self.video = video

    def handle(self, args):
        self.video.make_unwatermarked_video(
            'output.mp4',
            args.steps_dir,
            suffix='sofar',
            interpolate=False,
            fps_multiple=args.fps_multiple,
        )
