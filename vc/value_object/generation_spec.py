from dataclasses import dataclass
from typing import List
from flask_restplus import fields

from vc.api import api


@dataclass
class ImageSpec:
    texts: List[str]
    styles: List[str]
    iterations: int = 50
    epochs: int = 10
    x_shift: float = 0.
    y_shift: float = 0.
    z_shift: float = 0.05

    schema = api.model('Image Spec', {
        'texts': fields.List(fields.String, default_factory=list),
        'styles': fields.List(fields.String, default_factory=list),
        'iterations': fields.Integer(default=50),
        'epochs': fields.Integer(default=10),
        'x_shift': fields.Float(default=0.),
        'y_shift': fields.Float(default=0.),
        'z_shift': fields.Float(default=0.05),
    })


@dataclass
class VideoSpec(ImageSpec):
    pass


@dataclass
class GenerationSpec:
    images: List[ImageSpec] = None
    videos: List[VideoSpec] = None

    schema = api.model('Generation Spec', {
        'images': fields.List(fields.Nested(ImageSpec.schema)),
        'videos': fields.List(fields.Nested(VideoSpec.schema)),
    })
