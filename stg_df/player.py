import pygame

from .constants import (
    BLACK,
    GREEN,
    HEIGHT,
    RESPAWN_ANIMATION_TIME,
    RESPAWN_INVINCIBLE_TIME,
    RED,
    WHITE,
    WIDTH,
    YELLOW,
)
from .projectiles import Ammo, HomingAmmo


class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 25
        self.y = HEIGHT - 180

        self.fast_speed = 7
        self.slow_speed = 3

        self.shoot_cooldown = 0
        self.homing_cooldown = 0

        self.size = 50
        self.hitbox_radius = 3

        self.alive = True
        self.is_slow = False

        self.invincible_timer = RESPAWN_INVINCIBLE_TIME
        self.respawn_timer = 0

    def center_x(self):
        return self.x + self.size // 2

    def center_y(self):
        return self.y + self.size // 2

    def move(self, dx, dy):
        if not self.alive:
            return

        speed = self.slow_speed if self.is_slow else self.fast_speed
        self.x += dx * speed
        self.y += dy * speed

    def update(self):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1

            target_y = HEIGHT - 180
            if self.y > target_y:
                self.y -= 4

            if self.respawn_timer <= 0:
                self.alive = True
                self.invincible_timer = RESPAWN_INVINCIBLE_TIME

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.size:
            self.x = WIDTH - self.size

        if self.y < 0:
            self.y = 0
        elif self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.homing_cooldown > 0:
            self.homing_cooldown -= 1

    def can_shoot(self):
        return self.alive and self.shoot_cooldown <= 0

    def can_shoot_homing(self):
        return self.homing_cooldown <= 0

    def shoot(self, targets):
        bullets = []

        if self.is_slow:
            self.shoot_cooldown = 4
            offsets = [-18, -9, 9, 18]

            for offset in offsets:
                bullets.append(
                    Ammo(
                        x=self.center_x() + offset,
                        y=self.y,
                        vx=0,
                        vy=-12,
                        damage=1,
                        color=YELLOW,
                        owner="player",
                    )
                )
        else:
            self.shoot_cooldown = 8
            front_offsets = [-7, 7]

            for offset in front_offsets:
                bullets.append(
                    Ammo(
                        x=self.center_x() + offset,
                        y=self.y,
                        vx=0,
                        vy=-12,
                        damage=1,
                        color=YELLOW,
                        owner="player",
                    )
                )

            if self.can_shoot_homing():
                self.homing_cooldown = self.shoot_cooldown * 2

                bullets.append(
                    HomingAmmo(
                        x=self.x,
                        y=self.center_y(),
                        target_list=targets,
                        damage=1,
                        color=GREEN,
                        owner="player",
                    )
                )

                bullets.append(
                    HomingAmmo(
                        x=self.x + self.size,
                        y=self.center_y(),
                        target_list=targets,
                        damage=1,
                        color=GREEN,
                        owner="player",
                    )
                )

        return bullets

    def is_vulnerable(self):
        return self.alive and self.invincible_timer <= 0 and self.respawn_timer <= 0

    def die(self):
        self.alive = False

    def respawn(self):
        self.x = WIDTH // 2 - self.size // 2
        self.y = HEIGHT + 40
        self.alive = False
        self.respawn_timer = RESPAWN_ANIMATION_TIME
        self.invincible_timer = RESPAWN_INVINCIBLE_TIME
        self.shoot_cooldown = 0
        self.homing_cooldown = 0

    def draw(self, screen):
        if not self.alive and self.respawn_timer <= 0:
            return

        if self.invincible_timer > 0 or self.respawn_timer > 0:
            if (self.invincible_timer + self.respawn_timer) // 6 % 2 == 0:
                return

        self.draw_marisa(screen)

        if self.is_slow:
            self.draw_hitbox(screen)

    def draw_marisa(self, screen):
        cx = int(self.center_x())
        cy = int(self.center_y())
        x = int(self.x)
        y = int(self.y)

        # Wide witch hat.
        pygame.draw.ellipse(screen, WHITE, (x + 1, y + 4, self.size - 2, 13))
        pygame.draw.ellipse(screen, BLACK, (x + 4, y + 6, self.size - 8, 8))
        pygame.draw.polygon(
            screen,
            BLACK,
            [
                (cx - 16, y + 9),
                (cx - 2, y - 12),
                (cx + 17, y + 9),
            ],
        )
        pygame.draw.polygon(
            screen,
            WHITE,
            [
                (cx - 7, y + 1),
                (cx + 1, y - 7),
                (cx + 9, y + 2),
            ],
            2,
        )

        # Hair and face.
        hair = (255, 220, 95)
        skin = (255, 224, 190)
        pygame.draw.circle(screen, hair, (cx, y + 20), 13)
        pygame.draw.circle(screen, skin, (cx, y + 19), 8)
        pygame.draw.circle(screen, BLACK, (cx - 3, y + 18), 1)
        pygame.draw.circle(screen, BLACK, (cx + 3, y + 18), 1)

        # Black dress with white apron.
        pygame.draw.polygon(
            screen,
            BLACK,
            [
                (cx - 14, y + 30),
                (cx + 14, y + 30),
                (cx + 19, y + 48),
                (cx - 19, y + 48),
            ],
        )
        pygame.draw.polygon(
            screen,
            WHITE,
            [
                (cx - 6, y + 31),
                (cx + 6, y + 31),
                (cx + 10, y + 45),
                (cx - 10, y + 45),
            ],
        )
        pygame.draw.line(screen, WHITE, (cx - 18, y + 36), (cx - 28, y + 31), 3)
        pygame.draw.line(screen, WHITE, (cx + 18, y + 36), (cx + 28, y + 31), 3)

    def draw_hitbox(self, screen):
        center = (int(self.center_x()), int(self.center_y()))

        for radius, color in [
            (10, (90, 0, 0)),
            (8, (150, 20, 20)),
            (6, RED),
            (4, (255, 130, 130)),
        ]:
            pygame.draw.circle(screen, color, center, radius, 1)

        pygame.draw.circle(screen, WHITE, center, 4)
        pygame.draw.circle(screen, RED, center, self.hitbox_radius, 1)


# =========================
