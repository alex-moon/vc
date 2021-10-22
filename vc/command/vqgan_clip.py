from math import pi
from injector import inject

from vc.command.base import BaseCommand
from vc.service.vqgan_clip import VqganClipService, VqganClipOptions


class VqganClipCommand(BaseCommand):
    description = 'Runs vqgan_clip on an input file'
    args = [
        {
            'dest': 'output_file',
            'type': str,
            'help': 'Output file',
            'default': 'debug.png',
            'nargs': '?',
        },
        {
            'dest': 'prompt',
            'type': str,
            'help': 'Text prompts with : and | as usual',
            'default': 'parallel rusted train tracks | mineral : 0.4 | eugene atget',
            'nargs': '?',
        },
        {
            'dest': 'iterations',
            'type': int,
            'help': 'Iterations',
            'default': 200,
            'nargs': '?',
        }
    ]

    vqgan_clip: VqganClipService

    @inject
    def __init__(self, vqgan_clip: VqganClipService):
        self.vqgan_clip = vqgan_clip

    def handle(self, args):
        print('got %s %s' % (args.input_file, args.output_file))
        self.vqgan_clip.handle(VqganClipOptions(
            init_image=None,
            output_filename=args.output_file,
            prompts=args.prompt,
            max_iterations=args.iterations,
        ))
