import os
from dataclasses import dataclass

import numpy as np
from ISR.models import RRDN
from PIL import Image
from injector import inject

from vc.service import FileService


@dataclass
class IsrOptions:
    input_file: str = 'output.png'
    output_file: str = 'output-upscaled.png'


class IsrService:
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: IsrOptions):
        image = Image.open(args.input_file)
        image = image.convert('RGB')
        image_array = np.array(image)

        model = RRDN(weights='gans')
        result = model.predict(image_array)
        output = Image.fromarray(result)

        output.save(args.output_file)

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'isr-%s' % (
                    args.output_file
                )
            )
