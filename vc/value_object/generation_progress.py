from typing import Tuple
from dataclasses import dataclass


@dataclass
class GenerationProgress:
    steps_total: int
    steps_completed: int
    name: str
    result: Tuple[str, str] = None
    preview: str = None
    interim: Tuple[str, str] = None
