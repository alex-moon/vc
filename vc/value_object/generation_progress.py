from dataclasses import dataclass


@dataclass
class GenerationProgress:
    steps_total: int
    steps_completed: int
    name: str
    result: str = None
    preview: str = None
