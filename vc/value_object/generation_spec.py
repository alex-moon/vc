from typing import List
from dataclasses import dataclass, field
from flask_restplus import fields

from vc.api import api


@dataclass
class ImageSpec:
    prompts: str = None
    image_prompts: str = None
    max_iterations: int = 500
    display_freq: int = 50
    size: int = None
    init_image: str = None
    init_noise: str = 'gradient'
    init_weight: float = 0.
    clip_model: str = 'ViT-B/32'
    vqgan_config: str = f'checkpoints/vqgan_imagenet_f16_16384.yaml'
    vqgan_checkpoint: str = f'checkpoints/vqgan_imagenet_f16_16384.ckpt'
    noise_prompt_seeds: List[int] = field(default_factory=list)
    noise_prompt_weights: List[float] = field(default_factory=list)
    step_size: float = 0.1
    cutn: int = 32
    cut_pow: float = 1.
    seed: int = None
    optimiser: str = 'Adam'
    output: str = "output.png"
    make_video: bool = False
    cudnn_determinism: bool = False
    augments: str = None

    schema = api.model('Image Spec', {
        prompts: fields.String,
        image_prompts: fields.String,
        max_iterations: fields.Integer,
        display_freq: fields.Integer,
        size: fields.Integer,
        init_image: fields.String,
        init_noise: fields.String,
        init_weight: fields.Float,
        clip_model: fields.String,
        vqgan_config: fields.String,
        vqgan_checkpoint: fields.String,
        noise_prompt_seeds: fields.List(fields.Integer),
        noise_prompt_weights: fields.List(fields.Float),
        step_size: fields.Float,
        cutn: fields.Integer,
        cut_pow: fields.Float,
        seed: fields.Integer,
        optimiser: fields.String,
        output: fields.String,
        make_video: fields.Boolean,
        cudnn_determinism: fields.Boolean,
        augments: fields.String,
    })


@dataclass
class VideoSpec:
    schema = api.model('Video Spec', {

    })


@dataclass
class GenerationSpec:
    images: List = None
    videos: List = None

    schema = api.model('Generation Spec', {
        'images': fields.List(fields.Nested(ImageSpec.schema)),
        'videos': fields.List(fields.Nested(VideoSpec.schema)),
    })
