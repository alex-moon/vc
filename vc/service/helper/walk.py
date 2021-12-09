from dataclasses import dataclass
import random


@dataclass
class WalkTarget:
    x: float
    z: float
    pan: float
    y: float


class Walk:
    BOBBLE_TIME = 25
    x = 0.
    z = 0.
    pan = 0.
    y = 0.
    current_epoch = None
    target_epoch = None
    field = None

    @classmethod
    def target(cls):
        if cls.current_epoch == cls.target_epoch:
            cls.target_epoch = random.randint(25, 100)
            cls.current_epoch = 0
            cls.field = random.randint(0, 2)
            value = random.uniform(-2.0, 2.0)
            cls.x = value if cls.field == 0 else 0.
            cls.z = value if cls.field == 1 else 0.
            cls.pan = value if cls.field == 2 else 0.

        cls.current_epoch += 1
        return WalkTarget(
            x=cls.x,
            z=cls.z,
            pan=cls.pan,
            y=cls.get_y()
        )

    @classmethod
    def get_y(cls):
        if cls.field == 2:
            return 0.

        y_step = cls.current_epoch % cls.BOBBLE_TIME - 1
        return (cls.BOBBLE_TIME - y_step) / cls.BOBBLE_TIME - 0.5
