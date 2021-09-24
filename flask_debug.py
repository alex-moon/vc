from vc.service.inpainting import InpaintingService, InpaintingOptions
from vc import create_app, injector


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


app = create_app()
inpainting: InpaintingService = ClassLoader.load('vc.service.inpainting.InpaintingService')
inpainting.handle(InpaintingOptions(**{
    'input_file': 'output.png',
    'output_filename': 'debug.png',
    'crop_border': [0., 0., 0., 0.],
    'dynamic_fov': True,
}))
