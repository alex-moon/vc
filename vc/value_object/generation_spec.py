from typing import List
from dataclasses import dataclass, field
from flask_restplus import fields

from vc.service.vqgan_clip import VqganClipOptions
from vc.api import api


@dataclass
class ImageSpec(VqganClipOptions):
    # @todo not quite - we want our own spec that hides most of this
    schema = api.model('Image Spec', {
        'prompts': fields.String,
        'image_prompts': fields.String,
        'max_iterations': fields.Integer,
        'display_freq': fields.Integer,
        'size': fields.Integer,
        'init_image': fields.String,
        'init_noise': fields.String,
        'init_weight': fields.Float,
        'clip_model': fields.String,
        'vqgan_config': fields.String,
        'vqgan_checkpoint': fields.String,
        'noise_prompt_seeds': fields.List(fields.Integer),
        'noise_prompt_weights': fields.List(fields.Float),
        'step_size': fields.Float,
        'cutn': fields.Integer,
        'cut_pow': fields.Float,
        'seed': fields.Integer,
        'optimiser': fields.String,
        'output': fields.String,
        'make_video': fields.Boolean,
        'cudnn_determinism': fields.Boolean,
        'augments': fields.String,
    })


@dataclass
class VideoSpec:
    schema = api.model('Video Spec', {

    })


@dataclass
class GenerationSpec:
    images: List[ImageSpec] = None
    videos: List[VideoSpec] = None

    schema = api.model('Generation Spec', {
        'images': fields.List(fields.Nested(ImageSpec.schema)),
        'videos': fields.List(fields.Nested(VideoSpec.schema)),
    })
