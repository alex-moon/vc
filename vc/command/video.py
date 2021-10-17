from os import listdir
from os.path import isfile, join, splitext
from shutil import copyfile
from injector import inject

from vc.command.base import BaseCommand
from vc.service import VideoService
from vc.service.abme import AbmeService, AbmeOptions


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

    abme: AbmeService
    video: VideoService

    @inject
    def __init__(self, video: VideoService):
        self.video = video

    def handle(self, args):
        self.video.make_unwatermarked_video(
            'output.mp4',
            args.steps_dir,
            interpolate=True
        )
