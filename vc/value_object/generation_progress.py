from dataclasses import dataclass


@dataclass
class GenerationProgress:
    steps_total: int
    steps_completed: int
