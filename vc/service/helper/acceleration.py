class Acceleration:
    x = -0.001
    y = 0.001
    z = -0.001


class Multiplier:
    x = -0.01
    y = 0.01
    z = -0.01

    @classmethod
    def accelerate_x(cls, x, target):
        target = cls.x * target
        return x < target if target > 0 else x > target

    @classmethod
    def accelerate_y(cls, y, target):
        target = cls.y * target
        return y < target if target > 0 else y > target

    @classmethod
    def accelerate_z(cls, z, target):
        target = cls.z * target
        return z < target if target > 0 else z > target


class Zero:
    @classmethod
    def accelerate_x(cls, x, target):
        target = Multiplier.x * target
        return x > 0 if target > 0 else x < 0

    @classmethod
    def accelerate_y(cls, y, target):
        target = Multiplier.y * target
        return y > 0 if target > 0 else y < 0

    @classmethod
    def accelerate_z(cls, z, target):
        target = Multiplier.z * target
        return z > 0 if target > 0 else z < 0


class Velocity:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def accelerate(self, x_target, y_target, z_target):
        x_result = self.accelerate_x(x_target)
        y_result = self.accelerate_y(y_target)
        z_result = self.accelerate_z(z_target)
        return x_result or y_result or z_result

    def decelerate(self, x_target, y_target, z_target):
        x_result = self.decelerate_x(x_target)
        y_result = self.decelerate_y(y_target)
        z_result = self.decelerate_z(z_target)
        return x_result or y_result or z_result

    def accelerate_x(self, target):
        result = Multiplier.accelerate_x(self.x, target)
        if result:
            self.x += Acceleration.x
        return result

    def accelerate_y(self, target):
        result = Multiplier.accelerate_x(self.y, target)
        if result:
            self.y += Acceleration.y
        return result

    def accelerate_z(self, target):
        result = Multiplier.accelerate_z(self.z, target)
        if result:
            self.z += Acceleration.z
        return result

    def decelerate_x(self, target):
        result = Zero.accelerate_x(self.x, target)
        if result:
            self.x -= Acceleration.x
        return result

    def decelerate_y(self, target):
        result = Zero.accelerate_x(self.y, target)
        if result:
            self.y -= Acceleration.y
        return result

    def decelerate_z(self, target):
        result = Zero.accelerate_z(self.z, target)
        if result:
            self.z -= Acceleration.z
        return result

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

    def move(self, autodecelerate=False):
        accelerating = self.velocity.accelerate(
            self.x_target,
            self.y_target,
            self.z_target
        )

        if autodecelerate and not accelerating:
            self.velocity.decelerate(
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
