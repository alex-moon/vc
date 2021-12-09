from math import isclose


class Multiplier:
    x = -0.01
    y = 0.01
    z = -0.01

    @classmethod
    def accelerate_x(cls, x, target, transition):
        acceleration = abs(cls.x) / transition
        target = cls.x * target
        if isclose(x, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if x < target else -acceleration

    @classmethod
    def accelerate_y(cls, y, target, transition):
        acceleration = abs(cls.y) / transition
        target = cls.y * target
        if isclose(y, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if y < target else -acceleration

    @classmethod
    def accelerate_z(cls, z, target, transition):
        acceleration = abs(cls.z) / transition
        target = cls.z * target
        if isclose(z, target, abs_tol=acceleration * 0.5):
            return 0
        return acceleration if z < target else -acceleration


class Velocity:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def accelerate(self, x_target, y_target, z_target, transition):
        self.accelerate_x(x_target, transition)
        self.accelerate_y(y_target, transition)
        self.accelerate_z(z_target, transition)

    def accelerate_x(self, target, transition):
        self.x += Multiplier.accelerate_x(self.x, target, transition)

    def accelerate_y(self, target, transition):
        self.y += Multiplier.accelerate_y(self.y, target, transition)

    def accelerate_z(self, target, transition):
        self.z += Multiplier.accelerate_z(self.z, target, transition)

    def to_tuple(self):
        return self.x, self.y, self.z

    def moving(self, x_target, y_target, z_target):
        x_result = self.x > 0 if x_target * Multiplier.x > 0 else self.x <= 0
        y_result = self.y > 0 if y_target * Multiplier.y > 0 else self.y <= 0
        z_result = self.z > 0 if z_target * Multiplier.z > 0 else self.z <= 0
        return x_result or y_result or z_result


class Translate:
    velocity: Velocity
    x_target: float
    y_target: float
    z_target: float
    x = 0.
    y = 0.
    z = 0.
    transition = 20
    reset_threshold = 0.02

    def __init__(
        self,
        x_target: float,
        y_target: float,
        z_target: float,
        previous=None,
        transition=20
    ):
        self.x_target = x_target
        self.y_target = y_target
        self.z_target = z_target
        self.transition = transition

        if previous is not None:
            self.velocity = previous.velocity
            self.x = previous.x
            self.y = previous.y
            self.z = previous.z
        else:
            self.velocity = Velocity()

    def move(self):
        self.velocity.accelerate(
            self.x_target,
            self.y_target,
            self.z_target,
            self.transition
        )

        self.x += self.velocity.x
        self.y += self.velocity.y
        self.z += self.velocity.z

        return self.velocity.moving(
            self.x_target,
            self.y_target,
            self.z_target
        )

    def to_tuple(self):
        return self.x, self.y, self.z

    def reset(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def should_reset(self):
        return (
            abs(self.x) > self.reset_threshold
            or abs(self.y) > self.reset_threshold
            or abs(self.z) > self.reset_threshold
        )
