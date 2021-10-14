class BaseCommand:
    description: str
    args = []

    def run(self, args):
        self.handle(args)

    def handle(self, args):
        pass
