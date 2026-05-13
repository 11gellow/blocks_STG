import math

import pygame

from .constants import GREEN, HEIGHT, WIDTH, YELLOW


def lighter(color, amount=70):
    return tuple(min(255, value + amount) for value in color)


def darker(color, amount=55):
    return tuple(max(0, value - amount) for value in color)


class Ammo:
    def __init__(
        self,
        x,
        y,
        vx,
        vy,
        damage=1,
        color=YELLOW,
        owner="player",
        shape=None,
        radius=None,
        delay=0,
        length=None,
        width=None,
    ):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y

        self.vx = vx
        self.vy = vy

        self.damage = damage
        self.color = color
        self.owner = owner
        self.alive = True

        self.delay = delay
        self.age = 0
        self.trail = []

        if owner == "player":
            self.shape = shape or "rect"
            self.width = width or 5
            self.height = length or 12
            self.radius = radius or 4
            self.hit_radius = self.radius
        else:
            self.shape = shape or "orb"
            self.radius = radius or 7
            self.width = width or max(6, self.radius * 2)
            self.height = length or max(6, self.radius * 2)
            self.length = length or self.radius * 8
            self.hit_radius = max(3, int(self.radius * 0.58))

    def update(self):
        self.age += 1
        self.prev_x = self.x
        self.prev_y = self.y

        if self.delay > 0:
            self.delay -= 1
            self.trail.append((self.x - self.vx * 4, self.y - self.vy * 4))
            self.trail = self.trail[-8:]
            return

        self.trail.append((self.x, self.y))
        self.trail = self.trail[-8:]

        self.x += self.vx
        self.y += self.vy

        margin = max(self.width, self.height, self.radius * 2, getattr(self, "length", 0)) + 80
        if (
            self.x < -margin
            or self.x > WIDTH + margin
            or self.y < -margin
            or self.y > HEIGHT + margin
        ):
            self.alive = False

    def draw(self, screen):
        if self.owner == "player":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            return

        if self.shape == "laser":
            self.draw_laser(screen)
        elif self.shape == "delayed_laser":
            self.draw_delayed_laser(screen)
        elif self.shape == "needle":
            self.draw_needle(screen)
        elif self.shape == "petal":
            self.draw_petal(screen)
        elif self.shape == "star":
            self.draw_star(screen)
        else:
            self.draw_orb(screen)

    def draw_orb(self, screen):
        center = (int(self.x), int(self.y))
        pygame.draw.circle(screen, darker(self.color, 45), center, self.radius + 2)
        pygame.draw.circle(screen, self.color, center, self.radius)
        pygame.draw.circle(screen, lighter(self.color, 80), center, max(2, self.radius // 2))

    def draw_needle(self, screen):
        angle = math.atan2(self.vy, self.vx)
        forward = (math.cos(angle), math.sin(angle))
        side = (-forward[1], forward[0])
        length = max(18, self.radius * 5)
        half_w = max(3, self.radius * 0.55)
        tip = (self.x + forward[0] * length, self.y + forward[1] * length)
        tail = (self.x - forward[0] * length * 0.35, self.y - forward[1] * length * 0.35)
        points = [
            (int(tip[0]), int(tip[1])),
            (int(tail[0] + side[0] * half_w), int(tail[1] + side[1] * half_w)),
            (int(tail[0] - side[0] * half_w), int(tail[1] - side[1] * half_w)),
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.line(screen, lighter(self.color, 70), (int(tail[0]), int(tail[1])), (int(tip[0]), int(tip[1])), 2)

    def draw_petal(self, screen):
        rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 3)
        rect.center = (int(self.x), int(self.y))
        pygame.draw.ellipse(screen, self.color, rect)
        pygame.draw.ellipse(screen, lighter(self.color, 60), rect.inflate(-self.radius, -self.radius), 1)

    def draw_star(self, screen):
        points = []
        for i in range(10):
            radius = self.radius * (1.35 if i % 2 == 0 else 0.58)
            angle = math.radians(i * 36 + self.age * 4)
            points.append((int(self.x + math.cos(angle) * radius), int(self.y + math.sin(angle) * radius)))
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.circle(screen, lighter(self.color, 70), (int(self.x), int(self.y)), max(2, self.radius // 3))

    def draw_laser(self, screen):
        start, end = self.laser_segment()
        width = max(4, int(self.radius * 1.15))
        pygame.draw.line(screen, darker(self.color, 50), start, end, width + 5)
        pygame.draw.line(screen, self.color, start, end, width)
        pygame.draw.line(screen, lighter(self.color, 95), start, end, max(2, width // 2))

    def draw_delayed_laser(self, screen):
        start, end = self.laser_segment()

        if self.delay > 0:
            telegraph = max(1, self.radius // 2)
            for index, (tx, ty) in enumerate(self.trail):
                alpha_width = max(1, telegraph - index // 3)
                pygame.draw.circle(screen, darker(self.color, 35), (int(tx), int(ty)), alpha_width)
            pygame.draw.line(screen, darker(self.color, 70), start, end, 1)
            pygame.draw.circle(screen, lighter(self.color, 60), (int(self.x), int(self.y)), max(3, self.radius // 2), 1)
            return

        self.draw_laser(screen)

    def laser_segment(self):
        length = getattr(self, "length", self.radius * 8)
        speed = math.hypot(self.vx, self.vy)
        if speed == 0:
            dx, dy = 0, 1
        else:
            dx, dy = self.vx / speed, self.vy / speed

        start = (int(self.x - dx * length * 0.15), int(self.y - dy * length * 0.15))
        end = (int(self.x + dx * length), int(self.y + dy * length))
        return start, end

    def player_collision_radius(self):
        if self.delay > 0:
            return 0

        if self.shape in ("laser", "delayed_laser"):
            return max(3, int(self.radius * 0.45))

        if self.shape == "needle":
            return max(3, int(self.radius * 0.48))

        return self.hit_radius

    def collision_segment(self):
        if self.shape in ("laser", "delayed_laser") and self.delay <= 0:
            return self.laser_segment()

        return None


class HomingAmmo(Ammo):
    def __init__(self, x, y, target_list, damage=1, color=GREEN, owner="player"):
        homing_speed = 12 * 1.85

        super().__init__(
            x=x,
            y=y,
            vx=0,
            vy=-homing_speed,
            damage=damage,
            color=color,
            owner=owner,
            shape="orb",
            radius=5,
        )

        self.target_list = target_list
        self.speed = homing_speed

        self.width = 7
        self.height = 7

    def find_nearest_target(self):
        alive_targets = [target for target in self.target_list if target.alive]

        if not alive_targets:
            return None

        return min(
            alive_targets,
            key=lambda target: (
                (target.center_x() - self.x) ** 2
                + (target.center_y() - self.y) ** 2
            )
        )

    def update(self):
        target = self.find_nearest_target()

        if target is not None:
            dx = target.center_x() - self.x
            dy = target.center_y() - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance != 0:
                self.vx = dx / distance * self.speed
                self.vy = dy / distance * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed

        super().update()
