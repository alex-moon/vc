import sys
import argparse

from vc import create_app, injector
from vc import command


class ClassLoader:
    @classmethod
    def load(cls, class_name):
        class_instance = injector.get(
            cls.handle_import(class_name)
        )

        return class_instance

    @classmethod
    def handle_import(cls, name):
        components = name.split('.')
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod


class CommandLoader:
    commands = {
        'inpainting': command.InpaintingCommand
    }

    @classmethod
    def load(cls, key) -> command.BaseCommand:
        return ClassLoader.load(cls.commands[key])


if __name__ == '__main__':
    app = create_app()
    if len(sys.argv) < 2:
        print('Usage: %s <command> [args]' % sys.argv[0])
        exit()

    command = CommandLoader.load(sys.argv[1])
    parser = argparse.ArgumentParser(description=command.description)
    for arg in command.args:
        parser.add_argument(**arg)
    args = parser.parse_args()
    command.run(args)
