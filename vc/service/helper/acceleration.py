from math import isclose


class Acceleration:
    x = 0.0005
    y = 0.0005
    z = 0.0005


class Multiplier:
    x = -0.01
    y = 0.01
    z = -0.01

    @classmethod
    def accelerate_x(cls, x, target):
        target = cls.x * target
        if isclose(x, target, abs_tol=Acceleration.x * 0.5):
            return 0
        return Acceleration.x if x < target else -Acceleration.x

    @classmethod
    def accelerate_y(cls, y, target):
        target = cls.y * target
        if isclose(y, target, abs_tol=Acceleration.y * 0.5):
            return 0
        return Acceleration.y if y < target else -Acceleration.y

    @classmethod
    def accelerate_z(cls, z, target):
        target = cls.z * target
        if isclose(z, target, abs_tol=Acceleration.z * 0.5):
            return 0
        return Acceleration.z if z < target else -Acceleration.z


class Velocity:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def accelerate(self, x_target, y_target, z_target):
        self.accelerate_x(x_target)
        self.accelerate_y(y_target)
        self.accelerate_z(z_target)

    def accelerate_x(self, target):
        self.x += Multiplier.accelerate_x(self.x, target)

    def accelerate_y(self, target):
        self.y += Multiplier.accelerate_y(self.y, target)

    def accelerate_z(self, target):
        self.z += Multiplier.accelerate_z(self.z, target)

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

    def __init__(
        self,
        x_target: float,
        y_target: float,
        z_target: float,
        previous=None
    ):
        self.x_target = x_target
        self.y_target = y_target
        self.z_target = z_target

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
            self.z_target
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
