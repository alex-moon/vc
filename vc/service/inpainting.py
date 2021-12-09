import gc
import os
from dataclasses import dataclass, field
from typing import List

import cv2
import imageio
import numpy as np
import torch
import vispy
from injector import inject

from vc.service.file import FileService
from vc.service.helper.diagnosis import DiagnosisHelper as dh
from vc.service.helper.inpainting.bilateral_filtering import \
    sparse_bilateral_filtering
from vc.service.helper.inpainting.mesh import (
    write_ply,
    read_ply,
    output_3d_photo,
)
from vc.service.helper.inpainting.networks import (
    Inpaint_Color_Net,
    Inpaint_Depth_Net,
    Inpaint_Edge_Net,
)
from .helper.dimensions import DimensionsHelper
from .helper.midas import run_depth
from .helper.midas.utils import read_pfm
from .helper.utils import get_midas_sample, read_midas_depth


@dataclass
class InpaintingOptions:
    depth_edge_model_ckpt: str = 'checkpoints/edge-model.pth'
    depth_feat_model_ckpt: str = 'checkpoints/depth-model.pth'
    rgb_feat_model_ckpt: str = 'checkpoints/color-model.pth'
    midas_model_type: str = 'dpt_hybrid'  # use 'midas_v21_small' for faster
    fps: int = 40
    num_frames: int = 200
    x_shift: float = 0.00
    y_shift: float = 0.00
    z_shift: float = 0.00
    pan: float = 0.00
    tilt: float = 0.00
    roll: float = 0.00
    traj_type: str = 'double-straight-line'
    video_postfix: str = 'zoom-in'
    specific: str = ''
    longer_side_len: int = DimensionsHelper.width_small()
    input_file: str = 'output.png'
    output_filename: str = 'output.png'
    depth_folder: str = 'depth'
    mesh_folder: str = 'mesh'
    video_folder: str = None
    load_ply: bool = False
    save_ply: bool = True
    inference_video: bool = True
    offscreen_rendering: bool = False
    img_format: str = '.png'
    depth_format: str = '.pfm'
    require_midas: bool = True
    depth_threshold: float = 0.04
    ext_edge_threshold: float = 0.002
    sparse_iter: int = 5
    filter_size: List[int] = field(default_factory=lambda: [7, 7, 5, 5, 5])
    sigma_s: float = 4.0
    sigma_r: float = 0.5
    redundant_number: int = 12
    background_thickness: int = 70
    context_thickness: int = 140
    background_thickness_2: int = 70
    context_thickness_2: int = 70
    discount_factor: float = 1.00
    log_depth: bool = True
    largest_size: int = 512
    depth_edge_dilate: int = 10
    depth_edge_dilate_2: int = 5
    extrapolate_border: bool = True
    extrapolation_thickness: int = 60
    repeat_inpaint_edge: bool = True
    crop_border: List[float] = field(
        default_factory=lambda: [0., 0., 0., 0.]
    )
    anti_flickering: bool = False
    dynamic_fov: bool = True


class InpaintingService:
    model_paths = {
        "midas_v21_small": "checkpoints/model-small-70d6b9c8.pt",
        "midas_v21": "checkpoints/model-f6b98070.pt",
        "dpt_large": "checkpoints/dpt_large-midas-2f21e586.pt",
        "dpt_hybrid": "checkpoints/dpt_hybrid-midas-501f0c75.pt",
    }
    file_service: FileService

    @inject
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def handle(self, args: InpaintingOptions):
        if args.offscreen_rendering is True:
            vispy.use(app='egl')

        os.makedirs(args.mesh_folder, exist_ok=True)
        os.makedirs(args.depth_folder, exist_ok=True)

        if args.video_folder:
            os.makedirs(args.video_folder, exist_ok=True)

        sample = get_midas_sample(args)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        dh.debug('InpaintingService', 'running on device', device)

        dh.debug('InpaintingService', 'current source', sample['tgt_name'])
        mesh_fi = os.path.join(
            args.mesh_folder,
            sample['tgt_name'] + '.ply'
        )

        image = imageio.imread(sample['ref_img_fi'], pilmode="RGB")

        use_existing_ply = args.load_ply and os.path.exists(mesh_fi)
        if not use_existing_ply:
            midas_model_ckpt = self.model_paths[args.midas_model_type]
            dh.debug('InpaintingService', 'Running depth extraction')
            run_depth(
                sample['ref_img_fi'],
                args.depth_folder,
                midas_model_ckpt,
                args.midas_model_type
            )

        if 'npy' in args.depth_format:
            depth_file = np.load(sample['depth_fi'])
        elif 'pfm' in args.depth_format:
            depth_file, _ = read_pfm(sample['depth_fi'])
        else:
            depth_file = imageio.imread(sample['depth_fi'])

        args.output_h, args.output_w = depth_file.shape[:2]

        frac = args.longer_side_len / max(args.output_h, args.output_w)
        args.original_h = args.output_h = int(args.output_h * frac)
        args.original_w = args.output_w = int(args.output_w * frac)

        if image.ndim == 2:
            image = image[..., None].repeat(3, -1)
        if (
            np.sum(np.abs(image[..., 0] - image[..., 1])) == 0
            and np.sum(np.abs(image[..., 1] - image[..., 2])) == 0
        ):
            args.gray_image = True
        else:
            args.gray_image = False

        image = cv2.resize(
            image,
            (args.output_w, args.output_h),
            interpolation=cv2.INTER_AREA
        )

        depth = read_midas_depth(
            sample['depth_fi'],
            3.0,
            args.output_h,
            args.output_w
        )

        mean_loc_depth = depth[depth.shape[0] // 2, depth.shape[1] // 2]

        rt_info = False
        if not use_existing_ply:
            vis_photos, vis_depths = sparse_bilateral_filtering(
                depth,
                image,
                args,
                num_iter=args.sparse_iter
            )
            depth = vis_depths[-1]
            torch.cuda.empty_cache()

            dh.debug('InpaintingService', 'Start Running 3D_Photo', device)
            dh.debug('InpaintingService', 'Loading edge model')
            depth_edge_model = Inpaint_Edge_Net(init_weights=True)
            depth_edge_weight = torch.load(
                args.depth_edge_model_ckpt,
                map_location=torch.device(
                    device
                )
            )
            depth_edge_model.load_state_dict(depth_edge_weight)
            depth_edge_model = depth_edge_model.to(device)
            depth_edge_model.eval()

            dh.debug('InpaintingService', 'Loading depth model')
            depth_feat_model = Inpaint_Depth_Net()
            depth_feat_weight = torch.load(
                args.depth_feat_model_ckpt,
                map_location=torch.device(
                    device
                )
            )
            depth_feat_model.load_state_dict(depth_feat_weight, strict=True)
            depth_feat_model = depth_feat_model.to(device)
            depth_feat_model.eval()
            depth_feat_model = depth_feat_model.to(device)

            dh.debug('InpaintingService', 'Loading rgb model')
            rgb_model = Inpaint_Color_Net()
            rgb_feat_weight = torch.load(
                args.rgb_feat_model_ckpt,
                map_location=torch.device(device)
            )
            rgb_model.load_state_dict(rgb_feat_weight)
            rgb_model.eval()
            rgb_model = rgb_model.to(device)

            dh.debug(
                'InpaintingService',
                'Writing depth ply (and basically doing everything)'
            )
            rt_info = write_ply(
                image,
                depth,
                sample['int_mtx'],
                mesh_fi,
                args,
                rgb_model,
                depth_edge_model,
                depth_feat_model
            )

            if rt_info is False:
                dh.log('InpaintingService', 'Failed to write ply')
                return

            del depth
            del rgb_model
            del depth_edge_model
            del depth_feat_model

        if args.save_ply is True or args.load_ply is True:
            verts, colors, faces, height, width, hfov, vfov = read_ply(mesh_fi)
        elif rt_info is not False:
            verts, colors, faces, height, width, hfov, vfov = rt_info
        else:
            dh.log('InpaintingService', 'Could not determine ply')
            return

        del rt_info

        gc.collect()
        torch.cuda.empty_cache()

        dh.debug('InpaintingService', 'Making inpainting frame')

        top = (
            args.original_h // 2
            - sample['int_mtx'][1, 2]
            * args.output_h
        )
        left = (
            args.original_w // 2
            - sample['int_mtx'][0, 2]
            * args.output_w
        )
        down, right = top + args.output_h, left + args.output_w
        border = [int(xx) for xx in [top, down, left, right]]

        output_3d_photo(
            verts,
            colors,
            faces,
            height,
            width,
            sample['video_postfix'],
            sample['ref_pose'],
            args.video_folder,
            sample['int_mtx'],
            args,
            sample['tgts_pose'],
            args.original_h,
            args.original_w,
            border=border,
            mean_loc_depth=mean_loc_depth
        )

        if os.getenv('DEBUG_FILES'):
            return self.file_service.put(
                args.output_filename, 'inpainting-%s' % (
                    args.output_filename
                )
            )
