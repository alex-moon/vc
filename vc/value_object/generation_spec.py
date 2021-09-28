from dataclasses import dataclass
from typing import List

from flask_restplus import fields

from vc.api import api


@dataclass
class ImageSpec:
    texts: List[str] = None
    styles: List[str] = None
    iterations: int = 75
    upscale: bool = False

    schema = api.model('Image Spec', {
        'texts': fields.List(fields.String, default_factory=list),
        'styles': fields.List(fields.String, default_factory=list),
        'iterations': fields.Integer(default=75),
        'upscale': fields.Boolean(default=False),
    })


@dataclass
class VideoStepSpec(ImageSpec):
    init_iterations: int = 200
    epochs: int = 42
    x_velocity: float = 0.
    y_velocity: float = 0.
    z_velocity: float = 0.

    schema = api.model('Video Step Spec', ImageSpec.schema | {
        'init_iterations': fields.Integer(default=200),
        'epochs': fields.Integer(default=42),
        'x_velocity': fields.Float(default=0.),
        'y_velocity': fields.Float(default=0.),
        'z_velocity': fields.Float(default=0.),
    })


@dataclass
class VideoSpec:
    steps: List[VideoStepSpec]

    schema = api.model('Video Spec', {
        'steps': fields.List(fields.Nested(VideoStepSpec.schema))
    })


@dataclass
class GenerationSpec:
    images: List[ImageSpec] = None
    videos: List[VideoSpec] = None

    schema = api.model('Generation Spec', {
        'images': fields.List(fields.Nested(ImageSpec.schema)),
        'videos': fields.List(fields.Nested(VideoSpec.schema)),
    })
