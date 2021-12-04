import sys
import argparse

from vc import create_app, injector
from vc import command


class CommandLoader:
    commands = {
        'cgd': command.CgdCommand,
        'vqgan_clip': command.VqganClipCommand,
        'inpainting': command.InpaintingCommand,
        'esrgan': command.EsrganCommand,
        'rife': command.RifeCommand,
        'rife_steps': command.RifeStepsCommand,
        'video': command.VideoCommand,
    }

    @classmethod
    def load(cls, key) -> command.BaseCommand:
        return injector.get(cls.commands[key])


if __name__ == '__main__':
    app = create_app()
    if len(sys.argv) < 2:
        print('Usage: %s <command> [args]' % sys.argv[0])
        print('Available commands:')
        for key, command in CommandLoader.commands.items():
            print('%s: %s' % (key, command.description))
        exit()

    key = sys.argv[1]
    command = CommandLoader.load(key)
    parser = argparse.ArgumentParser(description=command.description)
    parser.add_argument(dest='key', type=str, default=key, nargs='?')
    for arg in command.args:
        parser.add_argument(**arg)
    args = parser.parse_args()
    command.run(args)
