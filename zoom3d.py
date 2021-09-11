import yaml

from vc.service.inpainting import InpaintingService, InpaintingOptions

config = yaml.load(open('argument.yml', 'r'))
args = InpaintingOptions(**config)
service = InpaintingService()
service.handle(args)
