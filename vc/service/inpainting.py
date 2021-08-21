import copy
import os
import time
import cv2
import imageio
import numpy as np
import torch
import vispy
from dataclasses import dataclass, field
from typing import List
from injector import inject
from tqdm import tqdm
import MiDaS.MiDaS_utils as MiDaS_utils
from MiDaS.monodepth_net import MonoDepthNet
from MiDaS.run import run_depth

from vc.service import FileService
from .helper.bilateral_filtering import sparse_bilateral_filtering
from .helper.boostmonodepth_utils import run_boostmonodepth
from .helper.mesh import write_ply, read_ply, output_3d_photo
from .helper.networks import (
    Inpaint_Color_Net,
    Inpaint_Depth_Net,
    Inpaint_Edge_Net,
)
from .helper.utils import get_MiDaS_samples, read_MiDaS_depth


@dataclass
class InpaintingOptions:
    depth_edge_model_ckpt: str = 'checkpoints/edge-model.pth'
    depth_feat_model_ckpt: str = 'checkpoints/depth-model.pth'
    rgb_feat_model_ckpt: str = 'checkpoints/color-model.pth'
    MiDaS_model_ckpt: str = 'MiDaS/model.pt'
    use_boostmonodepth: bool = True
    fps: int = 40
    num_frames: int = 200
    x_shift_range: List[float] = field(default_factory=lambda: [0.00])
    y_shift_range: List[float] = field(default_factory=lambda: [0.00])
    z_shift_range: List[float] = field(default_factory=lambda: [0.05])
    traj_types: List[str] = field(
        default_factory=lambda: ['double-straight-line']
    )
    video_postfix: List[str] = field(default_factory=lambda: ['zoom-in'])
    specific: str = ''
    longer_side_len: int = 400
    input_file: str = 'output.png'
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

        sample_list = get_MiDaS_samples(
            args,
            image_files=args.input_file
        )
        normal_canvas, all_canvas = None, None

        if isinstance(args.gpu_ids, int) and (args.gpu_ids >= 0):
            device = args.gpu_ids
        else:
            device = "cpu"

        print(f"running on device {device}")

        for idx in tqdm(range(len(sample_list))):
            depth = None
            sample = sample_list[idx]
            print("Current Source ==> ", sample['src_pair_name'])
            mesh_fi = os.path.join(
                args.mesh_folder,
                sample['src_pair_name'] + '.ply'
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
                    [sample['ref_img_fi']],
                    args.depth_folder,
                    args.MiDaS_model_ckpt,
                    MonoDepthNet,
                    MiDaS_utils,
                    target_w=640
                )

            if 'npy' in args.depth_format:
                args.output_h, args.output_w = np.load(
                    sample['depth_fi']
                ).shape[:2]
            else:
                args.output_h, args.output_w = imageio.imread(
                    sample['depth_fi']
                ).shape[:2]
            frac = args.longer_side_len / max(
                args.output_h,
                args.output_w
            )
            args.output_h, args.output_w = int(
                args.output_h * frac
            ), int(args.output_w * frac)
            args.original_h, args.original_w = args.output_h, \
                                               args.output_w
            if image.ndim == 2:
                image = image[..., None].repeat(3, -1)
            if np.sum(np.abs(image[..., 0] - image[..., 1])) == 0 and np.sum(
                np.abs(image[..., 1] - image[..., 2])
            ) == 0:
                args.gray_image = True
            else:
                args.gray_image = False
            image = cv2.resize(
                image, (args.output_w, args.output_h),
                interpolation=cv2.INTER_AREA
            )
            depth = read_MiDaS_depth(
                sample['depth_fi'], 3.0,
                args.output_h, args.output_w
            )
            mean_loc_depth = depth[depth.shape[0] // 2, depth.shape[1] // 2]
            if not (args.load_ply is True and os.path.exists(mesh_fi)):
                vis_photos, vis_depths = sparse_bilateral_filtering(
                    depth.copy(), image.copy(), args,
                    num_iter=args.sparse_iter, spdb=False
                )
                depth = vis_depths[-1]
                model = None
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
                graph = None

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
                    depth_edge_model,
                    depth_feat_model
                )

                if rt_info is False:
                    continue
                rgb_model = None
                color_feat_model = None
                depth_edge_model = None
                depth_feat_model = None
                torch.cuda.empty_cache()
            if args.save_ply is True or args.load_ply is True:
                verts, colors, faces, Height, Width, hFov, vFov = read_ply(
                    mesh_fi
                )
            else:
                verts, colors, faces, Height, Width, hFov, vFov = rt_info

            print(f"Making video at {time.time()}")
            videos_poses = copy.deepcopy(sample['tgts_poses'])
            video_basename = sample['tgt_name']
            top = (args.original_h // 2 - sample['int_mtx'][1, 2] *
                   args.output_h)
            left = (args.original_w // 2 - sample['int_mtx'][0, 2] *
                    args.output_w)
            down, right = top + args.output_h, left + args.output_w
            border = [int(xx) for xx in [top, down, left, right]]
            output_3d_photo(
                verts.copy(),
                colors.copy(),
                faces.copy(),
                copy.deepcopy(Height),
                copy.deepcopy(Width),
                sample['video_postfix'],
                copy.deepcopy(sample['ref_pose']),
                args.video_folder,
                copy.deepcopy(sample['int_mtx']),
                args,
                videos_poses,
                video_basename,
                args.original_h,
                args.original_w,
                border=border,
                normal_canvas=normal_canvas,
                all_canvas=all_canvas,
                mean_loc_depth=mean_loc_depth,
                mode='frame'
            )
