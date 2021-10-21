import os
from dataclasses import dataclass

import numpy as np
# from ISR.models import RRDN
from PIL import Image
from injector import inject

from vc.service import FileService


@dataclass
class IsrOptions:
    input_file: str = 'output.png'
    output_file: str = 'output-upscaled.png'


class IsrService:
    TARGET_WIDTH = int(os.getenv('SIZE_WIDTH_LG', 400))
    TARGET_HEIGHT = int(os.getenv('SIZE_HEIGHT_LG', 400))
    BORDER = 2

    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: IsrOptions):
        image = Image.open(args.input_file)
        image = image.convert('RGB')
        image_array = np.array(image)

        # model = RRDN(
        #     arch_params={'C': 4, 'D': 3, 'G': 32, 'G0': 32, 'T': 10, 'x': 4}
        # )
        # model.model.load_weights(
        #     'weights/rrdn-C4-D3-G32-G032-T10-x4_epoch299.hdf5'
        # )
        #
        # result = model.predict(image_array)
        result = image_array

        output = Image.fromarray(result)

        # Resize
        width = self.TARGET_WIDTH + 2 * self.BORDER
        height = self.TARGET_HEIGHT + 2 * self.BORDER
        output.thumbnail((width, height), Image.ANTIALIAS)

        # Crop
        output.crop(
            self.BORDER,
            self.BORDER,
            self.TARGET_WIDTH,
            self.TARGET_HEIGHT
        )

        # Save
        output.save(args.output_file)

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'isr-%s' % (
                    args.output_file
                )
            )
