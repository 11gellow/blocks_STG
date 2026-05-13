import math
import random
import pygame


class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.randint(25, 45)
        self.max_life = self.life
        self.size = random.randint(3, 7)
        self.color = color
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.94
        self.vy *= 0.94

        self.life -= 1

        if self.life <= 0:
            self.alive = False

    def draw(self, screen):
        if self.life <= 0:
            return

        ratio = self.life / self.max_life
        radius = max(1, int(self.size * ratio))

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            radius
        )


# =========================
