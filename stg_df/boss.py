import math
import pygame

from .constants import (
    BLUE,
    CYAN,
    GOLD,
    HEIGHT,
    LAVENDER,
    MAGENTA,
    ORANGE,
    PINK,
    PURPLE,
    SKY,
    WIDTH,
)
from .projectiles import Ammo


class Boss:
    def __init__(self, difficulty=1.0):
        self.size = 90
        self.x = WIDTH // 2 - self.size // 2
        self.y = -self.size

        self.target_y = 120
        self.enter_speed = 2

        self.alive = True
        self.active = False

        self.timer = 0
        self.shoot_cooldown = 0

        self.difficulty = difficulty

        self.phase = 0
        self.phase_names = [
            "Non-Spell: Velvet Rain",
            "Spell Card: Lotus Spiral",
            "Spell Card: Star Garden",
            "Final Spell: Moonlight Cage",
        ]

        # Boss 血量加厚
        base_healths = [360, 520, 680, 900]

        # Boss 血量随 Boss 难度大幅增长
        self.phase_healths = [
            int(value * (1 + (difficulty - 1) * 0.9))
            for value in base_healths
        ]
        self.health = self.phase_healths[self.phase]

    def center_x(self):
        return self.x + self.size // 2

    def center_y(self):
        return self.y + self.size // 2

    def current_phase_name(self):
        return self.phase_names[self.phase]

    def take_damage(self, damage):
        if not self.active:
            return "none"

        self.health -= damage

        if self.health <= 0:
            self.phase += 1

            if self.phase >= len(self.phase_healths):
                self.alive = False
                return "dead"

            self.health = self.phase_healths[self.phase]
            self.timer = 0
            self.shoot_cooldown = 80
            return "phase_clear"

        return "hit"

    def update(self):
        self.timer += 1

        if not self.active:
            self.y += self.enter_speed

            if self.y >= self.target_y:
                self.y = self.target_y
                self.active = True
                self.shoot_cooldown = 80

            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.x += math.sin(self.timer * 0.015) * 1.2

        if self.x < 40:
            self.x = 40
        elif self.x > WIDTH - self.size - 40:
            self.x = WIDTH - self.size - 40

    def can_shoot(self):
        return self.active and self.shoot_cooldown <= 0

    def shoot(self, player):
        # Boss 发弹频率魔鬼化
        interval_scale = max(0.28, 1 / self.difficulty)

        if self.phase == 0:
            self.shoot_cooldown = max(16, int(36 * interval_scale))
            return self.shoot_velvet_rain()

        if self.phase == 1:
            self.shoot_cooldown = max(20, int(54 * interval_scale))
            return self.shoot_lotus_spiral()

        if self.phase == 2:
            self.shoot_cooldown = max(24, int(68 * interval_scale))
            return self.shoot_star_garden(player)

        if self.phase == 3:
            self.shoot_cooldown = max(16, int(42 * interval_scale))
            return self.shoot_moonlight_cage(player)

        return []

    def shoot_velvet_rain(self):
        bullets = []
        count = min(42, 18 + int(self.difficulty * 7))
        base_y = self.center_y()

        for i in range(count):
            x_offset = (i - count // 2) * 20
            wave = math.sin((self.timer + i * 15) * 0.04) * (1.4 + self.difficulty * 0.2)

            bullets.append(
                Ammo(
                    x=self.center_x() + x_offset,
                    y=base_y,
                    vx=wave,
                    vy=1.8 + (i % 3) * 0.25 + self.difficulty * 0.12,
                    damage=1,
                    color=LAVENDER,
                    owner="enemy",
                )
            )

        return bullets

    def shoot_lotus_spiral(self):
        bullets = []

        layers = [
            {
                "count": min(34, 16 + int(self.difficulty * 5)),
                "speed": 1.45 + self.difficulty * 0.10,
                "color": CYAN,
                "offset": 0,
            },
            {
                "count": min(34, 16 + int(self.difficulty * 5)),
                "speed": 1.9 + self.difficulty * 0.10,
                "color": PURPLE,
                "offset": 11,
            },
            {
                "count": min(24, 8 + int(self.difficulty * 4)),
                "speed": 2.35 + self.difficulty * 0.10,
                "color": BLUE,
                "offset": 23,
            },
        ]

        rotate = self.timer * (4.2 + self.difficulty * 0.7)

        for layer in layers:
            count = layer["count"]
            speed = layer["speed"]
            color = layer["color"]
            offset = layer["offset"]

            for i in range(count):
                angle = 360 * i / count + rotate + offset
                vx, vy = self.velocity_from_angle(angle, speed)

                bullets.append(
                    Ammo(
                        x=self.center_x(),
                        y=self.center_y(),
                        vx=vx,
                        vy=vy,
                        damage=1,
                        color=color,
                        owner="enemy",
                    )
                )

        return bullets

    def shoot_star_garden(self, player):
        bullets = []

        points = 5
        rotate = self.timer * (3.5 + self.difficulty * 0.6)

        for ring in range(4):
            speed = 1.5 + ring * 0.38 + self.difficulty * 0.12
            color = [GOLD, ORANGE, MAGENTA, SKY][ring]

            for i in range(points * 2):
                angle = 360 * i / (points * 2) + rotate + ring * 12
                final_speed = speed if i % 2 == 0 else speed * 1.45
                vx, vy = self.velocity_from_angle(angle, final_speed)

                bullets.append(
                    Ammo(
                        x=self.center_x(),
                        y=self.center_y(),
                        vx=vx,
                        vy=vy,
                        damage=1,
                        color=color,
                        owner="enemy",
                    )
                )

        dx = player.center_x() - self.center_x()
        dy = player.center_y() - self.center_y()
        base_angle = math.degrees(math.atan2(dy, dx))

        aimed_offsets = [-42, -30, -18, -9, 0, 9, 18, 30, 42]
        speed = 2.2 + self.difficulty * 0.20

        for offset in aimed_offsets:
            vx, vy = self.velocity_from_angle(base_angle + offset, speed)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=SKY,
                    owner="enemy",
                )
            )

        return bullets

    def shoot_moonlight_cage(self, player):
        bullets = []

        rotate_a = self.timer * (5.0 + self.difficulty * 0.8)
        rotate_b = -self.timer * (3.2 + self.difficulty * 0.55)

        inner_count = min(54, 24 + int(self.difficulty * 8))
        for i in range(inner_count):
            angle = 360 * i / inner_count + rotate_a
            vx, vy = self.velocity_from_angle(angle, 1.65 + self.difficulty * 0.09)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=CYAN,
                    owner="enemy",
                )
            )

        outer_count = min(70, 32 + int(self.difficulty * 10))
        for i in range(outer_count):
            angle = 360 * i / outer_count + rotate_b
            vx, vy = self.velocity_from_angle(angle, 2.15 + self.difficulty * 0.09)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=MAGENTA,
                    owner="enemy",
                )
            )

        dx = player.center_x() - self.center_x()
        dy = player.center_y() - self.center_y()
        base_angle = math.degrees(math.atan2(dy, dx))

        aimed_offsets = [-54, -42, -30, -18, -9, 0, 9, 18, 30, 42, 54]

        for offset in aimed_offsets:
            vx, vy = self.velocity_from_angle(base_angle + offset, 2.55 + self.difficulty * 0.12)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=GOLD,
                    owner="enemy",
                )
            )

        return bullets

    def velocity_from_angle(self, angle_degree, speed):
        rad = math.radians(angle_degree)
        vx = math.cos(rad) * speed
        vy = math.sin(rad) * speed
        return vx, vy

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            PINK,
            (self.x, self.y, self.size, self.size)
        )


# =========================
