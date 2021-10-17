import os
from dataclasses import dataclass
from math import ceil

import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from injector import inject
from skimage.color import rgba2rgb
from skimage.io import imread
from torchvision.utils import save_image

from vc.service.file import FileService
from .helper import DiagnosisHelper as dh
from .helper.abme.model import SBMENet, ABMRNet, SynthesisNet
from .helper.abme.utils import warp


@dataclass
class AbmeOptions:
    first_file: str
    second_file: str
    output_file: str
    sbme_path: str = 'checkpoints/SBME_ckpt.pth'
    abmr_path: str = 'checkpoints/ABMR_ckpt.pth'
    syn_path: str = 'checkpoints/SynNet_ckpt.pth'
    DDP: bool = False


class AbmeService:
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: AbmeOptions):
        SBMNet = SBMENet()
        ABMNet = ABMRNet()
        SynNet = SynthesisNet(args)

        SBMNet.load_state_dict(torch.load(
            args.sbme_path,
            map_location='cpu'
        ))
        ABMNet.load_state_dict(torch.load(
            args.abmr_path,
            map_location='cpu'
        ))
        SynNet.load_state_dict(torch.load(
            args.syn_path,
            map_location='cpu'
        ))

        for param in SBMNet.parameters():
            param.requires_grad = False
        for param in ABMNet.parameters():
            param.requires_grad = False
        for param in SynNet.parameters():
            param.requires_grad = False

        SBMNet.cuda()
        ABMNet.cuda()
        SynNet.cuda()

        with torch.no_grad():
            img1 = imread(args.first_file)[:, :, :3]
            img2 = imread(args.second_file)[:, :, :3]
            frame1 = TF.to_tensor(img1).unsqueeze(0).cuda()
            frame3 = TF.to_tensor(img2).unsqueeze(0).cuda()

            H = frame1.shape[2]
            W = frame1.shape[3]

            # 4K video requires GPU memory of more than 24GB.
            # We recommend crop it into 4 regions with some margin.
            if H < 512:
                divisor = 64.
                D_factor = 1.
            else:
                divisor = 128.
                D_factor = 0.5

            H_ = int(ceil(H / divisor) * divisor * D_factor)
            W_ = int(ceil(W / divisor) * divisor * D_factor)

            frame1_ = F.interpolate(frame1, (H_, W_), mode='bicubic')
            frame3_ = F.interpolate(frame3, (H_, W_), mode='bicubic')

            SBM = SBMNet(torch.cat((frame1_, frame3_), dim=1))[0]
            SBM_ = F.interpolate(SBM, scale_factor=4, mode='bilinear') * 20.0

            frame2_1, Mask2_1 = warp(frame1_, SBM_ * (-1), return_mask=True)
            frame2_3, Mask2_3 = warp(frame3_, SBM_, return_mask=True)

            frame2_Anchor_ = (frame2_1 + frame2_3) / 2
            frame2_Anchor = frame2_Anchor_ + 0.5 * (
                    frame2_3 * (1 - Mask2_1) + frame2_1 * (1 - Mask2_3))

            Z = F.l1_loss(frame2_3, frame2_1, reduction='none').mean(1, True)
            Z_ = F.interpolate(Z, scale_factor=0.25, mode='bilinear') * (-20.0)

            ABM_bw, _ = ABMNet(
                torch.cat((frame2_Anchor, frame1_), dim=1),
                SBM * (-1),
                Z_.exp()
            )

            ABM_fw, _ = ABMNet(
                torch.cat((frame2_Anchor, frame3_), dim=1),
                SBM,
                Z_.exp()
            )

            SBM_ = F.interpolate(SBM, (H, W), mode='bilinear') * 20.0
            ABM_fw = F.interpolate(ABM_fw, (H, W), mode='bilinear') * 20.0
            ABM_bw = F.interpolate(ABM_bw, (H, W), mode='bilinear') * 20.0

            SBM_[:, 0, :, :] *= W / float(W_)
            SBM_[:, 1, :, :] *= H / float(H_)
            ABM_fw[:, 0, :, :] *= W / float(W_)
            ABM_fw[:, 1, :, :] *= H / float(H_)
            ABM_bw[:, 0, :, :] *= W / float(W_)
            ABM_bw[:, 1, :, :] *= H / float(H_)

            divisor = 8.
            H_ = int(ceil(H / divisor) * divisor)
            W_ = int(ceil(W / divisor) * divisor)

            Syn_inputs = torch.cat(
                (frame1, frame3, SBM_, ABM_fw, ABM_bw),
                dim=1
            )

            Syn_inputs = F.interpolate(Syn_inputs, (H_, W_), mode='bilinear')
            Syn_inputs[:, 6, :, :] *= float(W_) / W
            Syn_inputs[:, 7, :, :] *= float(H_) / H
            Syn_inputs[:, 8, :, :] *= float(W_) / W
            Syn_inputs[:, 9, :, :] *= float(H_) / H
            Syn_inputs[:, 10, :, :] *= float(W_) / W
            Syn_inputs[:, 11, :, :] *= float(H_) / H

            result = SynNet(Syn_inputs)

            result = F.interpolate(result, (H, W), mode='bicubic')

            dh.debug(
                'Writing ABME output frame:',
                os.path.abspath(args.output_file)
            )
            save_image(result, args.output_file)

        torch.cuda.empty_cache()

        if os.getenv('DEBUG_FILES'):
            self.file_service.put(
                args.output_file_file,
                'abme-%s' % (
                    args.output_file_file
                )
            )
