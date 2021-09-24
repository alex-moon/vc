import gc
import os
import time
from dataclasses import dataclass, field
from typing import List

import cv2
import imageio
import numpy as np
import torch
import vispy
from injector import inject

import MiDaS.MiDaS_utils as MiDaS_utils
from MiDaS.monodepth_net import MonoDepthNet
from MiDaS.run import run_depth
from vc.service.file import FileService
from .helper.bilateral_filtering import sparse_bilateral_filtering
from .helper.boostmonodepth_utils import run_boostmonodepth
from .helper.mesh import write_ply, read_ply, output_3d_photo
from .helper.networks import (
    Inpaint_Color_Net,
    Inpaint_Depth_Net,
    Inpaint_Edge_Net,
)
from .helper.utils import get_MiDaS_sample, read_MiDaS_depth


@dataclass
class InpaintingOptions:
    depth_edge_model_ckpt: str = 'checkpoints/edge-model.pth'
    depth_feat_model_ckpt: str = 'checkpoints/depth-model.pth'
    rgb_feat_model_ckpt: str = 'checkpoints/color-model.pth'
    MiDaS_model_ckpt: str = 'MiDaS/model.pt'
    use_boostmonodepth: bool = True
    fps: int = 40
    num_frames: int = 200
    x_shift: float = 0.00
    y_shift: float = 0.00
    z_shift: float = 0.00
    traj_type: str = 'double-straight-line'
    video_postfix: str = 'zoom-in'
    specific: str = ''
    longer_side_len: int = 400
    input_file: str = 'output.png'
    output_filename: str = 'output.png'
    depth_folder: str = 'depth'
    mesh_folder: str = 'mesh'
    video_folder: str = None
    load_ply: bool = False
    save_ply: bool = True
    inference_video: bool = True
    gpu_ids: int = 0
    offscreen_rendering: bool = False
    img_format: str = '.png'
    depth_format: str = '.npy'
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
        default_factory=lambda: [0.03, 0.03, 0.05, 0.03]
    )
    anti_flickering: bool = False
    dynamic_fov: bool = False


class InpaintingService:
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

        sample = get_MiDaS_sample(args)

        if isinstance(args.gpu_ids, int) and (args.gpu_ids >= 0):
            device = args.gpu_ids
        else:
            device = "cpu"

        print(f"running on device {device}")

        print("Current Source ==> ", sample['tgt_name'])
        mesh_fi = os.path.join(
            args.mesh_folder,
            sample['tgt_name'] + '.ply'
        )

        image = imageio.imread(sample['ref_img_fi'])

        print(f"Running depth extraction at {time.time()}")
        if args.use_boostmonodepth is True:
            run_boostmonodepth(
                sample['ref_img_fi'],
                args.depth_folder
            )
        elif args.require_midas is True:
            run_depth(
                sample['ref_img_fi'],
                args.depth_folder,
                args.MiDaS_model_ckpt,
                MonoDepthNet,
                MiDaS_utils
            )

        depth_file = (
            np.load(sample['depth_fi'])
            if 'npy' in args.depth_format
            else imageio.imread(sample['depth_fi'])
        )
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
        image = image.convert('RGB')

        depth = read_MiDaS_depth(
            sample['depth_fi'],
            3.0,
            args.output_h,
            args.output_w
        )

        mean_loc_depth = depth[depth.shape[0] // 2, depth.shape[1] // 2]

        rt_info = False
        if not (args.load_ply is True and os.path.exists(mesh_fi)):
            vis_photos, vis_depths = sparse_bilateral_filtering(
                depth,
                image,
                args,
                num_iter=args.sparse_iter
            )
            depth = vis_depths[-1]
            torch.cuda.empty_cache()

            print("Start Running 3D_Photo ...")
            print(f"Loading edge model at {time.time()}")
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

            print(f"Loading depth model at {time.time()}")
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

            print(f"Loading rgb model at {time.time()}")
            rgb_model = Inpaint_Color_Net()
            rgb_feat_weight = torch.load(
                args.rgb_feat_model_ckpt,
                map_location=torch.device(device)
            )
            rgb_model.load_state_dict(rgb_feat_weight)
            rgb_model.eval()
            rgb_model = rgb_model.to(device)

            print(
                f"Writing depth ply (and basically doing everything) at {time.time()}"
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
                print('Failed to write ply')
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
            print('Could not determine ply')
            return

        del rt_info

        gc.collect()
        torch.cuda.empty_cache()

        print(f"Making inpainting frame at {time.time()}")

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
