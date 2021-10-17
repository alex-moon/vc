from os import listdir
from os.path import isfile, join, splitext
from shutil import copyfile
from injector import inject

from vc.command.base import BaseCommand
from vc.service import VideoService
from vc.service.abme import AbmeService, AbmeOptions


class AbmeStepsCommand(BaseCommand):
    description = 'Runs abme on a steps files'
    args = [
        {
            'dest': 'steps_dir',
            'type': str,
            'help': 'Steps dir',
            'default': 'steps',
            'nargs': '?',
        },
        {
            'dest': 'usteps_dir',
            'type': str,
            'help': 'Usteps dir',
            'default': 'usteps',
            'nargs': '?',
        }
    ]

    abme: AbmeService
    video: VideoService

    @inject
    def __init__(self, abme: AbmeService, video: VideoService):
        self.abme = abme
        self.video = video

    def handle(self, args):
        input_files = [
            f
            for f
            in sorted(listdir(args.steps_dir))
            if isfile(join(args.steps_dir, f))
        ]

        for file in input_files:
            num, ext = splitext(file)
            outnum = int(num) * 2 - 1
            outfile = join(args.usteps_dir, f'{outnum:04}.png')
            infile = join(args.steps_dir, file)
            print('copying', infile, outfile)
            copyfile(infile, outfile)

            if int(num) > 1:
                last_outnum = outnum - 2
                new_outnum = outnum - 1
                first_file = join(args.usteps_dir, f'{last_outnum:04}.png')
                output_file = join(args.usteps_dir, f'{new_outnum:04}.png')
                second_file = outfile
                print('running abme', first_file, second_file, output_file)
                self.abme.handle(
                    AbmeOptions(
                        first_file=first_file,
                        second_file=second_file,
                        output_file=output_file,
                    )
                )

        self.video.make_unwatermarked_video(
            'debug.mp4',
            args.usteps_dir,
            fps_multiple=2
        )
