from vc import create_app


class ClassLoader:
    def loads(self, s, *args, **kwargs):
        [method, class_name, fnargs, fnkwargs] = json.loads(
            s.decode('utf-8'),
            *args,
            **kwargs
        )

        class_instance = self.binder.injector.get(
            self.handle_import(class_name)
        )

        return [
            method,
            class_instance,
            fnargs,
            fnkwargs
        ]

    # @see https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
    def handle_import(self, name):
        components = name.split('.')
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod


app = create_app()


