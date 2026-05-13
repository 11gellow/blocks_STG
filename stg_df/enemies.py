import math

import pygame

from .constants import (
    BLUE,
    CYAN,
    GOLD,
    GREEN,
    HEIGHT,
    LAVENDER,
    MAGENTA,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    SKY,
    WHITE,
    WIDTH,
    YELLOW,
)
from .projectiles import Ammo


ATTACK_PATTERNS = {
    "blue_needle": {"kind": "aimed_spread", "base": 86, "count": 3, "spread": 22, "speed": 3.8, "color": BLUE, "shape": "needle", "radius": 5},
    "violet_fan": {"kind": "fixed_fan", "base": 108, "count": 6, "start": 58, "end": 122, "speed": 3.4, "color": PURPLE, "shape": "petal", "radius": 8},
    "cyan_orbit": {"kind": "rotating_ring", "base": 150, "count": 12, "speed": 2.55, "rate": 4.2, "color": CYAN, "shape": "orb", "radius": 6},
    "orange_snipe": {"kind": "aimed_spread", "base": 106, "count": 3, "spread": 18, "speed": 4.0, "color": ORANGE, "shape": "laser", "radius": 7},
    "pink_cross": {"kind": "cross", "base": 124, "count": 2, "speed": 2.9, "rate": 5.0, "color": PINK, "shape": "orb", "radius": 10},
    "gold_lotus": {"kind": "flower", "base": 168, "petals": 5, "rings": 2, "speed": 2.25, "rate": 3.6, "color": GOLD, "shape": "petal", "radius": 9},
    "green_lane": {"kind": "lanes", "base": 108, "offsets": [-42, -14, 14, 42], "speed": 3.6, "color": GREEN, "shape": "orb", "radius": 5},
    "sky_twin": {"kind": "twin_fan", "base": 132, "count": 4, "spread": 48, "speed": 3.25, "color": SKY, "shape": "needle", "radius": 5},
    "magenta_arrow": {"kind": "arrow", "base": 118, "speed": 3.5, "color": MAGENTA, "shape": "needle", "radius": 6},
    "lavender_curtain": {"kind": "curtain", "base": 150, "count": 7, "width": 210, "speed": 2.9, "color": LAVENDER, "shape": "orb", "radius": 7},
    "red_spiral": {"kind": "spiral", "base": 94, "count": 3, "spacing": 34, "speed": 2.9, "rate": 10.0, "color": RED, "shape": "star", "radius": 8},
    "blue_backshot": {"kind": "backshot", "base": 132, "count": 5, "speed": 3.0, "color": BLUE, "shape": "needle", "radius": 5},
    "cyan_diamond": {"kind": "diamond", "base": 142, "speed": 2.7, "rate": 4.5, "color": CYAN, "shape": "laser", "radius": 6},
    "purple_pairs": {"kind": "paired_aim", "base": 112, "offsets": [-28, 28], "speeds": [3.0, 3.8], "color": PURPLE, "shape": "orb", "radius": 8},
    "orange_wall": {"kind": "sine_wall", "base": 158, "count": 8, "speed": 2.45, "wave": 1.3, "color": ORANGE, "shape": "orb", "radius": 11},
    "green_cage": {"kind": "cage", "base": 176, "count": 16, "gap": 4, "speed": 2.45, "rate": 2.5, "color": GREEN, "shape": "delayed_laser", "radius": 6, "delay": 38},
    "pink_bloom": {"kind": "flower", "base": 158, "petals": 6, "rings": 2, "speed": 2.15, "rate": -3.2, "color": PINK, "shape": "petal", "radius": 10},
    "gold_burst": {"kind": "ring", "base": 188, "count": 16, "speed": 2.7, "color": GOLD, "shape": "star", "radius": 8},
    "sky_comet": {"kind": "aimed_spread", "base": 92, "count": 2, "spread": 12, "speed": 4.45, "color": SKY, "shape": "laser", "radius": 6},
    "magenta_weave": {"kind": "spiral", "base": 108, "count": 4, "spacing": 48, "speed": 2.55, "rate": -8.5, "color": MAGENTA, "shape": "petal", "radius": 8},
    "lavender_arc": {"kind": "fixed_fan", "base": 130, "count": 8, "start": 42, "end": 138, "speed": 3.1, "color": LAVENDER, "shape": "orb", "radius": 6},
    "red_rake": {"kind": "lanes", "base": 110, "offsets": [-52, -26, 0, 26, 52], "speed": 3.9, "color": RED, "shape": "needle", "radius": 5},
    "blue_star": {"kind": "star", "base": 150, "points": 5, "speed": 2.75, "rate": 5.5, "color": BLUE, "shape": "star", "radius": 7},
    "cyan_split": {"kind": "paired_aim", "base": 124, "offsets": [-34, -12, 12, 34], "speeds": [2.8, 3.6], "color": CYAN, "shape": "orb", "radius": 5},
    "purple_mirror": {"kind": "mirror_fan", "base": 142, "count": 4, "spread": 58, "speed": 3.0, "color": PURPLE, "shape": "petal", "radius": 9},
    "orange_halo": {"kind": "ring", "base": 172, "count": 14, "speed": 2.25, "color": ORANGE, "shape": "orb", "radius": 10},
    "green_arrow": {"kind": "arrow", "base": 116, "speed": 3.6, "color": GREEN, "shape": "delayed_laser", "radius": 5, "delay": 30},
    "pink_spokes": {"kind": "cross", "base": 120, "count": 2, "speed": 2.85, "rate": -5.5, "color": PINK, "shape": "laser", "radius": 5},
    "gold_rain": {"kind": "curtain", "base": 140, "count": 9, "width": 250, "speed": 3.2, "color": GOLD, "shape": "orb", "radius": 6},
    "sky_flower": {"kind": "flower", "base": 172, "petals": 5, "rings": 3, "speed": 2.0, "rate": 4.0, "color": SKY, "shape": "petal", "radius": 8},
    "magenta_crown": {"kind": "fixed_fan", "base": 120, "count": 7, "start": 68, "end": 112, "speed": 3.6, "color": MAGENTA, "shape": "needle", "radius": 5},
    "lavender_lock": {"kind": "cage", "base": 168, "count": 18, "gap": 5, "speed": 2.35, "rate": -3.3, "color": LAVENDER, "shape": "delayed_laser", "radius": 7, "delay": 44},
    "red_fork": {"kind": "twin_fan", "base": 122, "count": 3, "spread": 36, "speed": 3.55, "color": RED, "shape": "needle", "radius": 6},
    "blue_stream": {"kind": "tri_stream", "base": 88, "speed": 3.9, "color": BLUE, "shape": "orb", "radius": 4},
    "cyan_shell": {"kind": "slow_fast_ring", "base": 180, "count": 10, "speed": 2.0, "color": CYAN, "shape": "orb", "radius": 10},
    "orange_net": {"kind": "sine_wall", "base": 150, "count": 10, "speed": 2.55, "wave": 1.9, "color": ORANGE, "shape": "delayed_laser", "radius": 5, "delay": 34},
}


ENEMY_TYPES = [
    {"name": "Scout Ruby", "color": RED, "accent": WHITE, "shape": "square", "size": 48, "health": 0.90, "attacks": ("blue_needle", "red_rake")},
    {"name": "Petal Violet", "color": PURPLE, "accent": LAVENDER, "shape": "diamond", "size": 52, "health": 1.00, "attacks": ("violet_fan", "purple_pairs")},
    {"name": "Orbit Cyan", "color": CYAN, "accent": BLUE, "shape": "circle", "size": 50, "health": 1.05, "attacks": ("cyan_orbit", "cyan_split")},
    {"name": "Needle Amber", "color": ORANGE, "accent": YELLOW, "shape": "triangle", "size": 54, "health": 1.10, "attacks": ("orange_snipe", "orange_halo")},
    {"name": "Cross Rose", "color": PINK, "accent": WHITE, "shape": "kite", "size": 56, "health": 1.15, "attacks": ("pink_cross", "pink_spokes")},
    {"name": "Lotus Gold", "color": GOLD, "accent": ORANGE, "shape": "hex", "size": 60, "health": 1.30, "attacks": ("gold_lotus", "gold_burst")},
    {"name": "Lane Jade", "color": GREEN, "accent": CYAN, "shape": "wing", "size": 50, "health": 1.00, "attacks": ("green_lane", "green_arrow")},
    {"name": "Twin Sky", "color": SKY, "accent": WHITE, "shape": "diamond", "size": 48, "health": 0.95, "attacks": ("sky_twin", "sky_comet")},
    {"name": "Arrow Magenta", "color": MAGENTA, "accent": PINK, "shape": "triangle", "size": 52, "health": 1.08, "attacks": ("magenta_arrow", "magenta_weave")},
    {"name": "Curtain Lavender", "color": LAVENDER, "accent": CYAN, "shape": "square", "size": 58, "health": 1.20, "attacks": ("lavender_curtain", "lavender_arc")},
    {"name": "Spiral Crimson", "color": RED, "accent": MAGENTA, "shape": "hex", "size": 54, "health": 1.15, "attacks": ("red_spiral", "red_fork")},
    {"name": "Backshot Azure", "color": BLUE, "accent": SKY, "shape": "wing", "size": 52, "health": 1.00, "attacks": ("blue_backshot", "blue_star")},
    {"name": "Diamond Aqua", "color": CYAN, "accent": WHITE, "shape": "diamond", "size": 56, "health": 1.20, "attacks": ("cyan_diamond", "cyan_shell")},
    {"name": "Mirror Grape", "color": PURPLE, "accent": PINK, "shape": "circle", "size": 50, "health": 1.05, "attacks": ("purple_mirror", "violet_fan")},
    {"name": "Wall Amber", "color": ORANGE, "accent": GOLD, "shape": "square", "size": 60, "health": 1.25, "attacks": ("orange_wall", "orange_net")},
    {"name": "Cage Jade", "color": GREEN, "accent": LAVENDER, "shape": "hex", "size": 58, "health": 1.30, "attacks": ("green_cage", "green_lane")},
    {"name": "Bloom Rose", "color": PINK, "accent": GOLD, "shape": "circle", "size": 56, "health": 1.18, "attacks": ("pink_bloom", "pink_cross")},
    {"name": "Burst Gold", "color": GOLD, "accent": WHITE, "shape": "kite", "size": 62, "health": 1.35, "attacks": ("gold_burst", "gold_rain")},
    {"name": "Comet Sky", "color": SKY, "accent": BLUE, "shape": "triangle", "size": 48, "health": 0.95, "attacks": ("sky_comet", "sky_flower")},
    {"name": "Weave Magenta", "color": MAGENTA, "accent": LAVENDER, "shape": "wing", "size": 54, "health": 1.10, "attacks": ("magenta_weave", "magenta_crown")},
    {"name": "Arc Lavender", "color": LAVENDER, "accent": WHITE, "shape": "diamond", "size": 58, "health": 1.22, "attacks": ("lavender_arc", "lavender_lock")},
    {"name": "Rake Crimson", "color": RED, "accent": ORANGE, "shape": "wing", "size": 50, "health": 1.04, "attacks": ("red_rake", "red_spiral")},
    {"name": "Star Azure", "color": BLUE, "accent": GOLD, "shape": "hex", "size": 56, "health": 1.16, "attacks": ("blue_star", "blue_stream")},
    {"name": "Split Aqua", "color": CYAN, "accent": SKY, "shape": "kite", "size": 54, "health": 1.12, "attacks": ("cyan_split", "cyan_orbit")},
    {"name": "Mirror Violet", "color": PURPLE, "accent": WHITE, "shape": "triangle", "size": 52, "health": 1.08, "attacks": ("purple_pairs", "purple_mirror")},
    {"name": "Halo Amber", "color": ORANGE, "accent": CYAN, "shape": "circle", "size": 56, "health": 1.18, "attacks": ("orange_halo", "orange_snipe")},
    {"name": "Arrow Jade", "color": GREEN, "accent": GOLD, "shape": "diamond", "size": 50, "health": 1.02, "attacks": ("green_arrow", "green_cage")},
    {"name": "Spoke Rose", "color": PINK, "accent": MAGENTA, "shape": "hex", "size": 54, "health": 1.14, "attacks": ("pink_spokes", "pink_bloom")},
    {"name": "Rain Gold", "color": GOLD, "accent": SKY, "shape": "square", "size": 60, "health": 1.28, "attacks": ("gold_rain", "gold_lotus")},
    {"name": "Flower Sky", "color": SKY, "accent": GREEN, "shape": "circle", "size": 58, "health": 1.20, "attacks": ("sky_flower", "sky_twin")},
    {"name": "Crown Magenta", "color": MAGENTA, "accent": WHITE, "shape": "kite", "size": 56, "health": 1.16, "attacks": ("magenta_crown", "magenta_arrow")},
    {"name": "Lock Lavender", "color": LAVENDER, "accent": RED, "shape": "hex", "size": 60, "health": 1.32, "attacks": ("lavender_lock", "lavender_curtain")},
    {"name": "Fork Crimson", "color": RED, "accent": YELLOW, "shape": "triangle", "size": 54, "health": 1.12, "attacks": ("red_fork", "red_rake")},
    {"name": "Stream Azure", "color": BLUE, "accent": WHITE, "shape": "square", "size": 50, "health": 1.04, "attacks": ("blue_stream", "blue_needle")},
    {"name": "Shell Aqua", "color": CYAN, "accent": GOLD, "shape": "wing", "size": 58, "health": 1.24, "attacks": ("cyan_shell", "cyan_diamond")},
    {"name": "Net Amber", "color": ORANGE, "accent": LAVENDER, "shape": "diamond", "size": 56, "health": 1.18, "attacks": ("orange_net", "orange_wall")},
]


def attacks_for_type(enemy_type_index):
    return ENEMY_TYPES[enemy_type_index % len(ENEMY_TYPES)]["attacks"]


def attack_for_type(enemy_type_index, wave_index=0):
    attacks = attacks_for_type(enemy_type_index)
    return attacks[wave_index % len(attacks)]


class Enemy:
    def __init__(self, x, y, difficulty=1.0, enemy_type=0, attack_pattern=None, movement=None, shot_phase=0):
        self.x = x
        self.y = y
        self.origin_x = x
        self.origin_y = y

        self.enemy_type = enemy_type % len(ENEMY_TYPES)
        self.style = ENEMY_TYPES[self.enemy_type]
        self.attack_pattern = attack_pattern or attack_for_type(self.enemy_type)
        self.movement = movement or {"kind": "straight", "vx": 0, "vy": 1.5}

        self.size = self.style["size"]
        self.speed = 1 + difficulty * 0.12
        self.health = int((8 + difficulty * 1.5) * self.style["health"])

        self.alive = True
        self.timer = 0
        self.difficulty = difficulty
        self.shoot_cooldown = 70 + shot_phase % 55

    def center_x(self):
        return self.x + self.size // 2

    def center_y(self):
        return self.y + self.size // 2

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.alive = False

    def update(self):
        self.timer += 1
        self.update_movement()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        margin = self.size + 80
        if (
            self.center_x() < -margin
            or self.center_x() > WIDTH + margin
            or self.center_y() < -margin * 2
            or self.center_y() > HEIGHT + margin
        ):
            self.alive = False

    def update_movement(self):
        kind = self.movement.get("kind", "straight")
        t = self.timer
        vx = self.movement.get("vx", 0)
        vy = self.movement.get("vy", 1.5) * self.speed

        if kind == "straight":
            self.x += vx
            self.y += vy
            return

        if kind == "sine":
            amp = self.movement.get("amp", 70)
            freq = self.movement.get("freq", 0.045)
            phase = self.movement.get("phase", 0)
            self.x = self.origin_x + vx * t + math.sin(t * freq + phase) * amp
            self.y = self.origin_y + vy * t
            return

        if kind == "curve":
            curve = self.movement.get("curve", 0.018)
            self.x = self.origin_x + vx * t + curve * t * t
            self.y = self.origin_y + vy * t
            return

        if kind == "hover":
            target_y = self.movement.get("target_y", 160)
            drift = self.movement.get("drift", 0)
            amp = self.movement.get("amp", 28)
            freq = self.movement.get("freq", 0.04)

            if self.y < target_y:
                self.y += vy
            else:
                self.x += drift
                self.y += 0.25 * self.speed

            self.x += math.sin(t * freq) * amp * 0.04
            return

        if kind == "bezier":
            duration = max(1, self.movement.get("duration", 150))
            p = min(1, t / duration)
            cx = self.movement.get("cx", self.origin_x)
            cy = self.movement.get("cy", HEIGHT * 0.3)
            ex = self.movement.get("ex", self.origin_x)
            ey = self.movement.get("ey", HEIGHT + self.size)
            self.x = (1 - p) * (1 - p) * self.origin_x + 2 * (1 - p) * p * cx + p * p * ex
            self.y = (1 - p) * (1 - p) * self.origin_y + 2 * (1 - p) * p * cy + p * p * ey

            if p >= 1:
                self.y += self.speed
            return

        if kind == "zigzag":
            amp = self.movement.get("amp", 64)
            period = max(1, self.movement.get("period", 48))
            segment = (t // period) % 2
            local = (t % period) / period
            wave = -1 + local * 2 if segment == 0 else 1 - local * 2
            self.x = self.origin_x + vx * t + wave * amp
            self.y = self.origin_y + vy * t
            return

        self.x += vx
        self.y += vy

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def shoot(self, player):
        pattern = ATTACK_PATTERNS.get(self.attack_pattern, ATTACK_PATTERNS["blue_needle"])
        base_cooldown = pattern.get("base", 90)
        type_rhythm = 1.0 + (self.enemy_type % 6) * 0.07
        difficulty_scale = max(0.88, 1.0 - (self.difficulty - 1.0) * 0.06)
        self.shoot_cooldown = max(70, int(base_cooldown * type_rhythm * difficulty_scale))
        return self.build_pattern(pattern, player)

    def build_pattern(self, pattern, player):
        kind = pattern["kind"]

        if kind == "aimed_spread":
            base = self.angle_to_player(player)
            return self.spread(base, pattern["count"], pattern["spread"], pattern["speed"], pattern["color"])

        if kind == "fixed_fan":
            return self.fixed_fan(pattern["start"], pattern["end"], pattern["count"], pattern["speed"], pattern["color"])

        if kind == "ring":
            return self.ring(pattern["count"], pattern["speed"], pattern["color"], self.timer * 0.5)

        if kind == "rotating_ring":
            return self.ring(pattern["count"], pattern["speed"], pattern["color"], self.timer * pattern["rate"])

        if kind == "twin_fan":
            base = self.angle_to_player(player)
            bullets = self.spread(base - pattern["spread"], pattern["count"], 24, pattern["speed"], pattern["color"])
            bullets.extend(self.spread(base + pattern["spread"], pattern["count"], 24, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "cross":
            bullets = []
            offset = self.timer * pattern["rate"]
            for arm in range(4):
                bullets.extend(self.spread(arm * 90 + offset, pattern["count"], 10, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "flower":
            bullets = []
            petals = pattern["petals"]
            for ring in range(pattern["rings"]):
                speed = pattern["speed"] + ring * 0.45
                offset = self.timer * pattern["rate"] + ring * 360 / (petals * 2)
                bullets.extend(self.ring(petals, speed, pattern["color"], offset))
            return bullets

        if kind == "lanes":
            bullets = []
            for offset in pattern["offsets"]:
                bullets.append(self.make_bullet(self.center_x() + offset, self.y + self.size, 0, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "arrow":
            base = self.angle_to_player(player)
            bullets = []
            for index, offset in enumerate([-42, -21, 0, 21, 42]):
                speed = pattern["speed"] + (2 - abs(index - 2)) * 0.25
                bullets.append(self.bullet_from_angle(base + offset, speed, pattern["color"]))
            return bullets

        if kind == "curtain":
            bullets = []
            count = pattern["count"]
            for i in range(count):
                t = i / max(1, count - 1)
                x = self.center_x() - pattern["width"] / 2 + pattern["width"] * t
                vx = (t - 0.5) * 0.7
                bullets.append(self.make_bullet(x, self.center_y(), vx, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "spiral":
            bullets = []
            start = self.timer * pattern["rate"]
            for i in range(pattern["count"]):
                bullets.append(self.bullet_from_angle(start + i * pattern["spacing"], pattern["speed"], pattern["color"]))
            return bullets

        if kind == "backshot":
            return self.fixed_fan(65, 115, pattern["count"], pattern["speed"], pattern["color"])

        if kind == "diamond":
            return self.ring(4, pattern["speed"], pattern["color"], 45 + self.timer * pattern["rate"])

        if kind == "paired_aim":
            base = self.angle_to_player(player)
            bullets = []
            for speed in pattern["speeds"]:
                for offset in pattern["offsets"]:
                    bullets.append(self.bullet_from_angle(base + offset, speed, pattern["color"]))
            return bullets

        if kind == "sine_wall":
            bullets = []
            count = pattern["count"]
            for i in range(count):
                x_offset = (i - count // 2) * 18
                vx = math.sin((self.timer + i * 17) * 0.06) * pattern["wave"]
                bullets.append(self.make_bullet(self.center_x() + x_offset, self.center_y(), vx, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "cage":
            bullets = []
            count = pattern["count"]
            offset = self.timer * pattern["rate"]
            gap = pattern["gap"]
            for i in range(count):
                if i % gap == 0:
                    continue
                bullets.append(self.bullet_from_angle(360 * i / count + offset, pattern["speed"], pattern["color"]))
            return bullets

        if kind == "mirror_fan":
            bullets = []
            bullets.extend(self.spread(90 - pattern["spread"] / 2, pattern["count"], pattern["spread"], pattern["speed"], pattern["color"]))
            bullets.extend(self.spread(90 + pattern["spread"] / 2, pattern["count"], pattern["spread"], pattern["speed"], pattern["color"]))
            return bullets

        if kind == "star":
            bullets = []
            points = pattern["points"] * 2
            for i in range(points):
                speed = pattern["speed"] if i % 2 == 0 else pattern["speed"] * 1.45
                bullets.append(self.bullet_from_angle(360 * i / points + self.timer * pattern["rate"], speed, pattern["color"]))
            return bullets

        if kind == "tri_stream":
            base = self.angle_to_player(player)
            return [
                self.bullet_from_angle(base - 12, pattern["speed"], pattern["color"]),
                self.bullet_from_angle(base, pattern["speed"] + 0.4, pattern["color"]),
                self.bullet_from_angle(base + 12, pattern["speed"], pattern["color"]),
            ]

        if kind == "slow_fast_ring":
            bullets = []
            bullets.extend(self.ring(pattern["count"], pattern["speed"], pattern["color"], self.timer * 2.0))
            bullets.extend(self.ring(pattern["count"], pattern["speed"] + 0.9, pattern["color"], self.timer * -2.4 + 9))
            return bullets

        return []

    def angle_to_player(self, player):
        dx = player.center_x() - self.center_x()
        dy = player.center_y() - self.center_y()
        return math.degrees(math.atan2(dy, dx))

    def fixed_fan(self, start, end, count, speed, color):
        bullets = []
        for i in range(count):
            t = i / max(1, count - 1)
            bullets.append(self.bullet_from_angle(start + (end - start) * t, speed, color))
        return bullets

    def spread(self, base_angle, count, spread, speed, color):
        bullets = []
        for i in range(count):
            t = i / max(1, count - 1)
            angle = base_angle - spread / 2 + spread * t
            bullets.append(self.bullet_from_angle(angle, speed, color))
        return bullets

    def ring(self, count, speed, color, offset=0):
        bullets = []
        for i in range(count):
            bullets.append(self.bullet_from_angle(360 * i / count + offset, speed, color))
        return bullets

    def bullet_from_angle(self, angle_degree, speed, color):
        vx, vy = self.velocity_from_angle(angle_degree, speed)
        return self.make_bullet(self.center_x(), self.center_y(), vx, vy, color)

    def make_bullet(self, x, y, vx, vy, color):
        pattern = ATTACK_PATTERNS.get(self.attack_pattern, ATTACK_PATTERNS["blue_needle"])
        shape = pattern.get("shape", "orb")
        radius = pattern.get("radius", 7)
        delay = pattern.get("delay", 0)
        length = pattern.get("length")

        if shape in ("laser", "delayed_laser") and length is None:
            length = 70 + radius * 10

        return Ammo(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            damage=1,
            color=color,
            owner="enemy",
            shape=shape,
            radius=radius,
            delay=delay,
            length=length,
        )

    def velocity_from_angle(self, angle_degree, speed):
        rad = math.radians(angle_degree)
        vx = math.cos(rad) * speed
        vy = math.sin(rad) * speed
        return vx, vy

    def draw(self, screen):
        color = self.style["color"]
        accent = self.style["accent"]
        shape = self.style["shape"]
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        cx = int(self.center_x())
        cy = int(self.center_y())
        radius = self.size // 2

        if shape == "circle":
            pygame.draw.circle(screen, color, (cx, cy), radius)
            pygame.draw.circle(screen, accent, (cx, cy), max(4, radius // 3), 2)
        elif shape == "diamond":
            points = [(cx, int(self.y)), (int(self.x + self.size), cy), (cx, int(self.y + self.size)), (int(self.x), cy)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.line(screen, accent, points[0], points[2], 2)
        elif shape == "triangle":
            points = [(cx, int(self.y + self.size)), (int(self.x), int(self.y)), (int(self.x + self.size), int(self.y))]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.circle(screen, accent, (cx, cy), max(3, radius // 4))
        elif shape == "wing":
            points = [
                (cx, int(self.y)),
                (int(self.x + self.size), int(self.y + self.size * 0.35)),
                (int(self.x + self.size * 0.66), int(self.y + self.size)),
                (cx, int(self.y + self.size * 0.72)),
                (int(self.x + self.size * 0.34), int(self.y + self.size)),
                (int(self.x), int(self.y + self.size * 0.35)),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.line(screen, accent, (cx, int(self.y + 6)), (cx, int(self.y + self.size - 8)), 2)
        elif shape == "kite":
            points = [(cx, int(self.y)), (int(self.x + self.size * 0.85), cy), (cx, int(self.y + self.size)), (int(self.x + self.size * 0.15), cy)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.circle(screen, accent, (cx, cy), max(4, radius // 4), 2)
        elif shape == "hex":
            points = []
            for i in range(6):
                angle = math.radians(60 * i + 30)
                points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, accent, points[::2], 2)
        else:
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, accent, rect.inflate(-self.size // 3, -self.size // 3), 2)
