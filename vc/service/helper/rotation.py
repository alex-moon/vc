from math import isclose, pi

from transforms3d import euler


class RotateAcceleration:
    tilt = 0.0009
    pan = 0.0009
    roll = 0.0009


class Multiplier:
    tilt = -(2 * pi / 360)
    pan = -(2 * pi / 360)
    roll = -(2 * pi / 360)

    @classmethod
    def accelerate_tilt(cls, tilt, target):
        target = cls.tilt * target
        if isclose(tilt, target, abs_tol=RotateAcceleration.tilt * 0.5):
            return 0
        return RotateAcceleration.tilt if tilt < target else -RotateAcceleration.tilt

    @classmethod
    def accelerate_pan(cls, pan, target):
        target = cls.pan * target
        if isclose(pan, target, abs_tol=RotateAcceleration.pan * 0.5):
            return 0
        return RotateAcceleration.pan if pan < target else -RotateAcceleration.pan

    @classmethod
    def accelerate_roll(cls, roll, target):
        target = cls.roll * target
        if isclose(roll, target, abs_tol=RotateAcceleration.roll * 0.5):
            return 0
        return RotateAcceleration.roll if roll < target else -RotateAcceleration.roll


class RotateVelocity:
    def __init__(self):
        self.tilt = 0.
        self.pan = 0.
        self.roll = 0.

    def accelerate(self, tilt_target, pan_target, roll_target):
        self.accelerate_tilt(tilt_target)
        self.accelerate_pan(pan_target)
        self.accelerate_roll(roll_target)

    def accelerate_tilt(self, target):
        self.tilt += Multiplier.accelerate_tilt(self.tilt, target)

    def accelerate_pan(self, target):
        self.pan += Multiplier.accelerate_pan(self.pan, target)

    def accelerate_roll(self, target):
        self.roll += Multiplier.accelerate_roll(self.roll, target)

    def to_tuple(self):
        return self.tilt, self.pan, self.roll

    def rotating(self, tilt_target, pan_target, roll_target):
        tilt_result = self.tilt > 0 if tilt_target * Multiplier.tilt > 0 else self.tilt <= 0
        pan_result = self.pan > 0 if pan_target * Multiplier.pan > 0 else self.pan <= 0
        roll_result = self.roll > 0 if roll_target * Multiplier.roll > 0 else self.roll <= 0
        return tilt_result or pan_result or roll_result


class Rotate:
    velocity: RotateVelocity
    tilt_target: float
    pan_target: float
    roll_target: float
    tilt = 0.
    pan = 0.
    roll = 0.

    def __init__(
        self,
        tilt_target: float,
        pan_target: float,
        roll_target: float,
        previous=None
    ):
        self.tilt_target = tilt_target
        self.pan_target = pan_target
        self.roll_target = roll_target

        if previous is not None:
            self.velocity = previous.velocity
            self.tilt = previous.tilt
            self.pan = previous.pan
            self.roll = previous.roll
        else:
            self.velocity = RotateVelocity()

    def rotate(self):
        self.velocity.accelerate(
            self.tilt_target,
            self.pan_target,
            self.roll_target
        )

        self.tilt += self.velocity.tilt
        self.pan += self.velocity.pan
        self.roll += self.velocity.roll

        return self.velocity.rotating(
            self.tilt_target,
            self.pan_target,
            self.roll_target
        )

    def to_tuple(self):
        return self.tilt, self.pan, self.roll

    def reset(self):
        self.tilt = 0.
        self.pan = 0.
        self.roll = 0.
