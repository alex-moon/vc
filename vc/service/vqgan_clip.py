import math
import os
import sys
from dataclasses import dataclass
from injector import inject

# pip install taming-transformers works with Gumbel, but does not work with coco etc
# appending the path works with Gumbel, but gives ModuleNotFoundError: No module named 'transformers' for coco etc
sys.path.append('taming-transformers')

#import taming.modules

import torch
from torch.nn import functional as F

torch.backends.cudnn.benchmark = False		# NR: True is a bit faster, but can lead to OOM. False is more deterministic.
#torch.use_deterministic_algorithms(True)	# NR: grid_sampler_2d_backward_cuda does not have a deterministic implementation

import numpy as np

from PIL import ImageFile, Image

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass
class VqganClipOptions:
    prompts: str = None
    image_prompts: str = []
    max_iterations: int = 500
    display_freq: int = 50
    size: int = [400, 400]
    init_image: str = None
    init_noise: str = 'pixels'
    init_weight: float = 0.
    clip_model: str = 'ViT-B/32'
    vqgan_config: str = f'checkpoints/vqgan_imagenet_f16_16384.yaml'
    vqgan_checkpoint: str = f'checkpoints/vqgan_imagenet_f16_16384.ckpt'
    noise_prompt_seeds: int = []
    noise_prompt_weights: float = []
    step_size: float = 0.1
    cutn: int = 32
    cut_pow: float = 1.
    seed: int = None
    optimiser: str = 'Adam'
    output: str = "output.png"
    make_video: bool = False
    cudnn_determinism: bool = False
    augments: str = []


class VqganClipService:
    @inject
    def __init__(self):
        pass

    def handle(self, args: VqganClipOptions):
        if args.cudnn_determinism:
            torch.backends.cudnn.deterministic = True

        if not args.augments:
            args.augments = [['Af', 'Pe', 'Ji', 'Er']]

        # Split text prompts using the pipe character
        if args.prompts:
            args.prompts = [phrase.strip() for phrase in
                            args.prompts.split("|")]

        # Split target images using the pipe character
        if args.image_prompts:
            args.image_prompts = args.image_prompts.split("|")
            args.image_prompts = [image.strip() for image in args.image_prompts]

        # Make video steps directory
        if args.make_video:
            if not os.path.exists('steps'):
                os.mkdir('steps')

    def sinc(self, x):
        return torch.where(
            x != 0,
            torch.sin(math.pi * x) / (math.pi * x),
            x.new_ones([])
        )

    def lanczos(self, x, a):
        cond = torch.logical_and(-a < x, x < a)
        out = torch.where(cond, self.sinc(x) * self.sinc(x / a), x.new_zeros([]))
        return out / out.sum()

    def ramp(self, ratio, width):
        n = math.ceil(width / ratio + 1)
        out = torch.empty([n])
        cur = 0
        for i in range(out.shape[0]):
            out[i] = cur
            cur += ratio
        return torch.cat([-out[1:].flip([0]), out])[1:-1]

    # NR: Testing with different intital images
    def random_noise_image(self, w, h):
        random_image = Image.fromarray(
            np.random.randint(0, 255, (w, h, 3), dtype=np.dtype('uint8')))
        return random_image

    # create initial gradient image
    def gradient_2d(self, start, stop, width, height, is_horizontal):
        if is_horizontal:
            return np.tile(np.linspace(start, stop, width), (height, 1))
        else:
            return np.tile(np.linspace(start, stop, height), (width, 1)).T

    def gradient_3d(self, width, height, start_list, stop_list, is_horizontal_list):
        result = np.zeros((height, width, len(start_list)), dtype=float)

        for i, (start, stop, is_horizontal) in enumerate(
            zip(start_list, stop_list, is_horizontal_list)):
            result[:, :, i] = self.gradient_2d(start, stop, width, height, is_horizontal)

        return result

    def random_gradient_image(self, w, h):
        array = self.gradient_3d(w, h, (0, 0, np.random.randint(0, 255)), (
        np.random.randint(1, 255), np.random.randint(2, 255),
        np.random.randint(3, 128)), (True, False, False))
        random_image = Image.fromarray(np.uint8(array))
        return random_image

    # Not used?
    def resample(self, input, size, align_corners=True):
        n, c, h, w = input.shape
        dh, dw = size

        input = input.view([n * c, 1, h, w])

        if dh < h:
            kernel_h = self.lanczos(self.ramp(dh / h, 2), 2).to(input.device, input.dtype)
            pad_h = (kernel_h.shape[0] - 1) // 2
            input = F.pad(input, (0, 0, pad_h, pad_h), 'reflect')
            input = F.conv2d(input, kernel_h[None, None, :, None])

        if dw < w:
            kernel_w = self.lanczos(self.ramp(dw / w, 2), 2).to(input.device, input.dtype)
            pad_w = (kernel_w.shape[0] - 1) // 2
            input = F.pad(input, (pad_w, pad_w, 0, 0), 'reflect')
            input = F.conv2d(input, kernel_w[None, None, None, :])

        input = input.view([n, c, h, w])
        return F.interpolate(
            input,
            size,
            mode='bicubic',
            align_corners=align_corners
        )
