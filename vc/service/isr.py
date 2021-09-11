import os
from dataclasses import dataclass

import numpy as np
from ISR.models import RDN
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
        img = Image.open(args.input_file)
        lr_img = np.array(img)

        rdn = RDN(weights='psnr-small')
        sr_img = rdn.predict(lr_img)
        output = Image.fromarray(sr_img)
        output.save(args.output_file)

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'visr-%s' % (
                    args.output_file
                )
            )
