from typing import List
from dataclasses import dataclass


@dataclass
class GenerationSpec:
    videos: List = None
    images: List = None
