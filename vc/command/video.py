from injector import inject

from vc.command.base import BaseCommand
from vc.service import VideoService


class VideoCommand(BaseCommand):
    description = 'Makes a video from steps files'
    args = [
        {
            'dest': 'steps_dir',
            'type': str,
            'help': 'Steps dir',
            'default': 'steps',
            'nargs': '?',
        },
        {
            'dest': 'interpolate',
            'action': 'store_true',
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
            fps_multiple=4 if not args.interpolate else 1,
            interpolate=args.interpolate
        )
