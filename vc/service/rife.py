import os
import warnings
from dataclasses import dataclass

import cv2
import torch
from injector import inject
from torch.nn import functional as F

from vc.service.file import FileService
from .helper.rife.model.RIFE_HDv3 import Model
from .helper.diagnosis import DiagnosisHelper as dh

warnings.filterwarnings("ignore")

@dataclass
class RifeOptions:
    first_file: str = 'first.png'
    second_file: str = 'second.png'
    output_file: str = 'output.png'
    model_dir: str = 'checkpoints'
    exp: int = 4
    ratio: float = 0
    rthreshold: float = 0.02
    rmaxcycles: int = 8


class RifeService:
    file_service: FileService
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: RifeOptions):
        with torch.no_grad():
            model = Model()
            model.load_model(args.model_dir, -1)
            dh.debug('RifeService', 'loaded v3.x HD model.')

            model.eval()
            model.device()

            img0 = cv2.imread(args.first_file, cv2.IMREAD_UNCHANGED)
            img1 = cv2.imread(args.second_file, cv2.IMREAD_UNCHANGED)
            img0 = (torch.tensor(img0.transpose(2, 0, 1)).to(self.device) / 255.).unsqueeze(0)
            img1 = (torch.tensor(img1.transpose(2, 0, 1)).to(self.device) / 255.).unsqueeze(0)

            n, c, h, w = img0.shape
            ph = ((h - 1) // 32 + 1) * 32
            pw = ((w - 1) // 32 + 1) * 32
            padding = (0, pw - w, 0, ph - h)
            img0 = F.pad(img0, padding)
            img1 = F.pad(img1, padding)

            mid = model.inference(img0, img1)

            dh.debug('RifeService', 'writing RIFE image', args.output_file)
            cv2.imwrite(
                args.output_file,
                (mid[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w]
            )

        torch.cuda.empty_cache()

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file,
                'rife-%s' % (
                    args.output_file
                )
            )
