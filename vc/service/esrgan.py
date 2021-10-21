import os
from dataclasses import dataclass

import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from injector import inject

from vc.service.file import FileService
from vc.service.helper.esrgan import RealESRGANer
from vc.service.helper.diagnosis import DiagnosisHelper as dh


@dataclass
class EsrganOptions:
    input_file: str = 'output.png'
    model_path: str = 'checkpoints/RealESRGAN_x4plus.pth'
    output_file: str = 'output.png'
    netscale: int = 4
    outscale: float = 4
    suffix: str = 'out'
    tile: int = 0
    tile_pad: int = 10
    pre_pad: int = 0
    half: bool = False
    block: int = 23


class EsrganService:
    TARGET_WIDTH = int(os.getenv('SIZE_WIDTH_LG'))
    TARGET_HEIGHT = int(os.getenv('SIZE_HEIGHT_LG'))
    BORDER = 2

    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: EsrganOptions):
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=args.block,
            num_grow_ch=32,
            scale=args.netscale
        )

        upsampler = RealESRGANer(
            scale=args.netscale,
            model_path=args.model_path,
            model=model,
            tile=args.tile,
            tile_pad=args.tile_pad,
            pre_pad=args.pre_pad,
            half=args.half
        )

        img = cv2.imread(args.input_file, cv2.IMREAD_UNCHANGED)

        h, w = img.shape[0:2]
        if max(h, w) > 1000 and args.netscale == 4:
            dh.log('EsrganService', 'The input image is large, try X2 model for better performance.')
        if max(h, w) < 500 and args.netscale == 2:
            dh.log('EsrganService', 'The input image is small, try X4 model for better performance.')

        try:
            output, _ = upsampler.enhance(img, outscale=args.outscale)
        except Exception as error:
            dh.log('EsrganService', 'Error', error)
            dh.log('EsrganService', 'hint: try smaller value for tile', args.tile)
            raise error

        # Resize
        width = self.TARGET_WIDTH + 2 * self.BORDER
        height = self.TARGET_HEIGHT + 2 * self.BORDER
        output = cv2.resize(output, (width, height), interpolation=cv2.INTER_AREA)

        # Crop
        start = self.BORDER
        end = -self.BORDER
        output = output[start:end, start:end]

        # Convert to RGB
        output = cv2.cvtColor(output, cv2.COLOR_RGBA2RGB)

        # Save
        cv2.imwrite(args.output_file, output)

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'esrgan-%s' % (
                    args.output_file
                )
            )
