import os
from dataclasses import dataclass

import numpy as np
from ISR.models import RRDN
from PIL import Image
from injector import inject

from vc.service import FileService


@dataclass
class IsrOptions:
    output_file: str = 'output.png'
    input_file: str = 'output.png'


class IsrService:
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: IsrOptions):
        image = Image.open(args.input_file)
        image = image.convert('RGB')
        pil_image = np.array(image)

        model = RRDN(weights='gans')
        result = model.predict(pil_image)
        output = Image.fromarray(result)

        # @todo intended size?
        # output.resize((width, height), Image.LANCZOS)
        output.thumbnail(image.size, Image.ANTIALIAS)
        output.save(args.output_file)

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'visr-%s' % (
                    args.output_file
                )
            )
