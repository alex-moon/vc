from dataclasses import dataclass
from typing import List, Optional

from flask_restplus import fields

from vc.api import api


@dataclass
class ImageSpec:
    texts: List[str] = None
    styles: List[str] = None
    ground: Optional[str] = None
    iterations: int = 200
    upscale: bool = False

    schema = api.model('Image Spec', {
        'texts': fields.List(fields.String, default_factory=list),
        'styles': fields.List(fields.String, default_factory=list),
        'ground': fields.String,
        'iterations': fields.Integer(default=200),
        'upscale': fields.Boolean(default=False),
    })


@dataclass
class VideoStepSpec(ImageSpec):
    iterations: int = 20
    interpolate: bool = False
    init_iterations: int = 200
    epochs: int = 42
    transition: int = 20
    x_velocity: float = 0.
    y_velocity: float = 0.
    z_velocity: float = 0.
    pan_velocity: float = 0.
    tilt_velocity: float = 0.
    roll_velocity: float = 0.
    random_walk: bool = False

    schema = api.model('Video Step Spec', {
        'texts': fields.List(fields.String, default_factory=list),
        'styles': fields.List(fields.String, default_factory=list),
        'ground': fields.String,
        'iterations': fields.Integer(default=20),
        'upscale': fields.Boolean(default=False),
        'interpolate': fields.Boolean(default=False),
        'init_iterations': fields.Integer(default=200),
        'epochs': fields.Integer(default=42),
        'transition': fields.Integer(default=20),
        'x_velocity': fields.Float(default=0.),
        'y_velocity': fields.Float(default=0.),
        'z_velocity': fields.Float(default=0.),
        'pan_velocity': fields.Float(default=0.),
        'tilt_velocity': fields.Float(default=0.),
        'roll_velocity': fields.Float(default=0.),
        'random_walk': fields.Boolean(default=False),
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
