from injector import inject

from vc.command.base import BaseCommand
from vc.service.cgd import CgdService, CgdOptions


class CgdCommand(BaseCommand):
    description = 'Runs cgd on an input file'
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
            'default': 'A stunning professional photograph of a primitive connected network of wooden huts and gathering places built among the treetops at varying heights and connected by boardwalks and ladders, the setting sun casting pink and red on the clouds in the sky. | cinematic masterpiece | post-production',
            'nargs': '?',
        }
    ]

    cgd: CgdService

    @inject
    def __init__(self, cgd: CgdService):
        self.cgd = cgd

    def handle(self, args):
        self.cgd.handle(CgdOptions(
            init_image=None,
            output_filename=args.output_file,
            prompts=args.prompt,
        ))
