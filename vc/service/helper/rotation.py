from math import isclose, pi


class Multiplier:
    tilt = -(2 * pi / 360)
    pan = -(2 * pi / 360)
    roll = -(2 * pi / 360)

    @classmethod
    def accelerate_tilt(cls, tilt, target, transition):
        acceleration = abs(cls.tilt) / transition  # target or cls.tilt?
        target = cls.tilt * target
        if isclose(tilt, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if tilt < target else -acceleration

    @classmethod
    def accelerate_pan(cls, pan, target, transition):
        acceleration = abs(cls.pan) / transition  # target or cls.pan?
        target = cls.pan * target
        if isclose(pan, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if pan < target else -acceleration

    @classmethod
    def accelerate_roll(cls, roll, target, transition):
        acceleration = abs(cls.roll) / transition  # target or cls.roll?
        target = cls.roll * target
        if isclose(roll, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if roll < target else -acceleration


class RotateVelocity:
    def __init__(self):
        self.tilt = 0.
        self.pan = 0.
        self.roll = 0.

    def accelerate(self, tilt_target, pan_target, roll_target, transition):
        self.accelerate_tilt(tilt_target, transition)
        self.accelerate_pan(pan_target, transition)
        self.accelerate_roll(roll_target, transition)

    def accelerate_tilt(self, target, transition):
        self.tilt += Multiplier.accelerate_tilt(self.tilt, target, transition)

    def accelerate_pan(self, target, transition):
        self.pan += Multiplier.accelerate_pan(self.pan, target, transition)

    def accelerate_roll(self, target, transition):
        self.roll += Multiplier.accelerate_roll(self.roll, target, transition)

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
    transition = 20
    reset_threshold = 0.02

    def __init__(
        self,
        tilt_target: float,
        pan_target: float,
        roll_target: float,
        previous=None,
        transition=20
    ):
        self.tilt_target = tilt_target
        self.pan_target = pan_target
        self.roll_target = roll_target
        self.transition = transition

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
            self.roll_target,
            self.transition
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

    def should_reset(self):
        return (
            abs(self.tilt) > self.reset_threshold
            or abs(self.pan) > self.reset_threshold
            or abs(self.roll) > self.reset_threshold
        )
