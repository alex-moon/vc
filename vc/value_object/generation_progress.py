from dataclasses import dataclass


@dataclass
class GenerationProgress:
    steps_total: int
    steps_completed: int
    name: str
    preview: str = None
    result: str = None
    result_watermarked: str = None
    interim: str = None
    interim_watermarked: str = None

