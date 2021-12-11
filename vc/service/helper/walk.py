from dataclasses import dataclass
import random
from typing import List


@dataclass
class WalkTarget:
    x: float
    z: float
    pan: float
    y: float


@dataclass
class Movement:
    key: str
    field: str
    sign: int
    p: float


class Walk:
    BOBBLE_TIME = 30

    MOVEMENTS: List[Movement] = [
        Movement(
            key='forward',
            field='z',
            sign=1,
            p=0.3,
        ),
        Movement(
            key='turn left',
            field='pan',
            sign=-1,
            p=0.2,
        ),
        Movement(
            key='turn right',
            field='pan',
            sign=1,
            p=0.2,
        ),
        Movement(
            key='strafe left',
            field='x',
            sign=-1,
            p=0.1,
        ),
        Movement(
            key='strafe right',
            field='x',
            sign=1,
            p=0.1,
        ),
        Movement(
            key='backward',
            field='z',
            sign=-1,
            p=0.1,
        ),
    ]

    x = 0.
    z = 0.
    pan = 0.
    y = 0.

    current_epoch = None
    target_epoch = None
    movement: Movement

    @classmethod
    def target(cls):
        if cls.current_epoch == cls.target_epoch:
            cls.target_epoch = random.randint(60, 200)
            cls.current_epoch = 0

            p = 0.
            choice = random.random()
            for movement in cls.MOVEMENTS:
                if choice < movement.p + p:
                    cls.movement = movement
                    break
                p += movement.p

            value = random.gauss(0.7, 0.5)

            cls.x = (
                cls.movement.sign * value
                if cls.movement.field == 'x'
                else 0.
            )
            cls.z = (
                cls.movement.sign * value
                if cls.movement.field == 'z'
                else 0.
            )
            cls.pan = (
                cls.movement.sign * value
                if cls.movement.field == 'pan'
                else 0.
            )

        cls.current_epoch += 1
        return WalkTarget(
            x=cls.x + cls.bobble_x(),
            z=cls.z,
            pan=cls.pan,
            y=cls.y + cls.bobble_y()
        )

    @classmethod
    def bobble_y(cls):
        if cls.movement.field == 'pan':
            return 0.

        y_step = cls.current_epoch % cls.BOBBLE_TIME - 1
        return (cls.BOBBLE_TIME - y_step) / cls.BOBBLE_TIME - 0.5

    @classmethod
    def bobble_x(cls):
        if cls.movement.field == 'pan':
            return 0.

        double_bobble = cls.BOBBLE_TIME * 2
        double_x = cls.current_epoch % double_bobble - 1
        x_step = double_x % cls.BOBBLE_TIME
        return (
            x_step
            if x_step == double_x
            else cls.BOBBLE_TIME - x_step
        ) / cls.BOBBLE_TIME - 0.5
