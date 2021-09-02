from dataclasses import dataclass
from typing import List

from flask_restplus import fields

from vc.api import api


@dataclass
class ImageSpec:
    texts: List[str] = None
    styles: List[str] = None
    iterations: int = 500
    epochs: int = 1
    x_shift: float = 0.
    y_shift: float = 0.
    z_shift: float = 0.

    schema = api.model('Image Spec', {
        'texts': fields.List(fields.String, default_factory=list),
        'styles': fields.List(fields.String, default_factory=list),
        'iterations': fields.Integer(default=50),
        'epochs': fields.Integer(default=10),
        'x_shift': fields.Float(default=0.),
        'y_shift': fields.Float(default=0.),
        'z_shift': fields.Float(default=0.),
    })


@dataclass
class VideoSpec:
    steps: List[ImageSpec]

    schema = api.model('Video Spec', {
        'steps': fields.List(fields.Nested(ImageSpec.schema))
    })


@dataclass
class GenerationSpec:
    images: List[ImageSpec] = None
    videos: List[VideoSpec] = None

    schema = api.model('Generation Spec', {
        'images': fields.List(fields.Nested(ImageSpec.schema)),
        'videos': fields.List(fields.Nested(VideoSpec.schema)),
    })
