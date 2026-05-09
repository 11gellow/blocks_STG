import math
import sys
import os
import random
import pygame


# =========================
# 基础配置
# =========================

WIDTH = 700
HEIGHT = 960
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (80, 160, 255)
GREEN = (80, 255, 120)
PURPLE = (190, 100, 255)
CYAN = (80, 255, 255)
ORANGE = (255, 170, 80)
PINK = (255, 100, 180)
MAGENTA = (255, 80, 220)
LAVENDER = (180, 140, 255)
SKY = (100, 220, 255)
GOLD = (255, 220, 100)

INITIAL_LIVES = 20
RESPAWN_INVINCIBLE_TIME = 180
RESPAWN_ANIMATION_TIME = 90

ENEMY_SCORE = 1000
BOSS_PHASE_SCORE = 20000
BOSS_CLEAR_SCORE = 100000

BASE_BOSS_KILL_REQUIREMENT = 45


# =========================
# 玩家
# =========================

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 25
        self.y = HEIGHT - 180

        self.fast_speed = 7
        self.slow_speed = 3

        self.shoot_cooldown = 0
        self.homing_cooldown = 0

        self.size = 50
        self.hitbox_radius = 5

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

        pygame.draw.rect(
            screen,
            WHITE,
            (self.x, self.y, self.size, self.size)
        )

        if self.is_slow:
            pygame.draw.circle(
                screen,
                GREEN,
                (int(self.center_x()), int(self.center_y())),
                self.hitbox_radius
            )


# =========================
# 子弹
# =========================

class Ammo:
    def __init__(self, x, y, vx, vy, damage=1, color=YELLOW, owner="player"):
        self.x = x
        self.y = y

        self.vx = vx
        self.vy = vy

        self.damage = damage
        self.color = color
        self.owner = owner

        self.alive = True

        if owner == "player":
            self.width = 5
            self.height = 12
        else:
            self.width = 8
            self.height = 8

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if (
            self.x < -self.width
            or self.x > WIDTH
            or self.y < -self.height
            or self.y > HEIGHT
        ):
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (self.x, self.y, self.width, self.height)
        )


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

        self.x += self.vx
        self.y += self.vy

        if (
            self.x < -self.width
            or self.x > WIDTH
            or self.y < -self.height
            or self.y > HEIGHT
        ):
            self.alive = False


# =========================
# 特效
# =========================

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
# 小怪
# =========================

class Enemy:
    def __init__(self, x, y, difficulty=1.0):
        self.x = x
        self.y = y

        self.size = 66

        # 小怪难度温和增长，不要太夸张
        self.speed = 1 + difficulty * 0.12
        self.health = int(8 + difficulty * 1.5)

        self.alive = True
        self.timer = 0
        self.difficulty = difficulty

        self.pattern = random.choice([
            "straight",
            "fan",
            "circle",
            "aimed",
        ])

        self.shoot_cooldown = random.randint(25, 65)

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
        self.y += self.speed

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.y > HEIGHT:
            self.alive = False

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def shoot(self, player):
        if self.pattern == "straight":
            self.shoot_cooldown = max(35, int(55 / self.difficulty))
            return self.shoot_straight()

        if self.pattern == "fan":
            self.shoot_cooldown = max(50, int(85 / self.difficulty))
            return self.shoot_fan()

        if self.pattern == "circle":
            self.shoot_cooldown = max(70, int(120 / self.difficulty))
            return self.shoot_circle()

        if self.pattern == "aimed":
            self.shoot_cooldown = max(45, int(75 / self.difficulty))
            return self.shoot_aimed(player)

        return []

    def shoot_straight(self):
        bullets = []
        offsets = [-18, 0, 18]
        speed = 3.8 + self.difficulty * 0.18

        for offset in offsets:
            bullets.append(
                Ammo(
                    x=self.center_x() + offset,
                    y=self.y + self.size,
                    vx=0,
                    vy=speed,
                    damage=1,
                    color=BLUE,
                    owner="enemy",
                )
            )

        return bullets

    def shoot_fan(self):
        bullets = []

        count = min(9, 7 + int(self.difficulty))
        speed = 3.8 + self.difficulty * 0.15
        start_angle = 50
        end_angle = 130

        for i in range(count):
            t = i / (count - 1)
            angle = start_angle + (end_angle - start_angle) * t
            vx, vy = self.velocity_from_angle(angle, speed)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=PURPLE,
                    owner="enemy",
                )
            )

        return bullets

    def shoot_circle(self):
        bullets = []

        count = min(18, 14 + int(self.difficulty * 1.5))
        speed = 2.8 + self.difficulty * 0.12
        rotate = self.timer * 5

        for i in range(count):
            angle = 360 * i / count + rotate
            vx, vy = self.velocity_from_angle(angle, speed)

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

        return bullets

    def shoot_aimed(self, player):
        bullets = []

        dx = player.center_x() - self.center_x()
        dy = player.center_y() - self.center_y()

        base_angle = math.degrees(math.atan2(dy, dx))

        angles = [-18, 0, 18]
        speed = 3.8 + self.difficulty * 0.18

        for offset in angles:
            vx, vy = self.velocity_from_angle(base_angle + offset, speed)

            bullets.append(
                Ammo(
                    x=self.center_x(),
                    y=self.center_y(),
                    vx=vx,
                    vy=vy,
                    damage=1,
                    color=ORANGE,
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
            RED,
            (self.x, self.y, self.size, self.size)
        )


# =========================
# Boss
# =========================

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
# 游戏总控
# =========================

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        pygame.mixer.init()

        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        music_path = os.path.join(base_path, "badapple.mp3")
        pygame.mixer.music.load(music_path) 
        pygame.mixer.music.set_volume(0.5)      
        pygame.mixer.music.play(-1)    

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny STG")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 60)

        self.player = Player()
        self.ammos = []
        self.enemies = []
        self.effects = []
        self.boss = None

        self.spawn_timer = 0

        self.score = 0
        self.lives = INITIAL_LIVES
        self.stage_number = 1

        # 拆成两套难度：
        # 小怪难度温和增长
        # Boss 难度魔鬼增长
        self.enemy_difficulty = 1.0
        self.boss_difficulty = 1.0

        self.kill_count = 0
        self.boss_kill_requirement = BASE_BOSS_KILL_REQUIREMENT

        self.stage = "normal"
        self.result_timer = 0

        self.debug_mode = False
        self.debug_input_active = False
        self.debug_text = ""

        self.running = True

               # -1 表示循环播放

    # -------------------------
    # 事件处理
    # -------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.debug_input_active = True
                    self.debug_text = ""

                elif self.debug_input_active:
                    if event.key == pygame.K_RETURN:
                        if self.debug_text.lower() == "debug":
                            self.debug_mode = True

                        self.debug_input_active = False
                        self.debug_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        self.debug_text = self.debug_text[:-1]

                    elif event.key == pygame.K_ESCAPE:
                        self.debug_input_active = False
                        self.debug_text = ""

                    else:
                        if event.unicode:
                            self.debug_text += event.unicode

                elif self.stage == "game_over":
                    if event.key == pygame.K_r:
                        self.restart_game()

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    # -------------------------
    # 输入处理
    # -------------------------

    def handle_input(self):
        if self.stage == "game_over":
            return

        keys = pygame.key.get_pressed()

        self.player.is_slow = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.player.move(dx, dy)

        if keys[pygame.K_z] and self.player.can_shoot():
            targets = self.get_player_targets()
            new_ammos = self.player.shoot(targets)
            self.ammos.extend(new_ammos)

    def get_player_targets(self):
        targets = [enemy for enemy in self.enemies if enemy.alive]

        if self.boss is not None and self.boss.alive:
            targets.append(self.boss)

        return targets

    # -------------------------
    # 游戏流程
    # -------------------------

    def restart_game(self):
        self.player = Player()
        self.ammos = []
        self.enemies = []
        self.effects = []
        self.boss = None

        self.spawn_timer = 0

        self.score = 0
        self.lives = INITIAL_LIVES
        self.stage_number = 1

        self.enemy_difficulty = 1.0
        self.boss_difficulty = 1.0

        self.kill_count = 0
        self.boss_kill_requirement = BASE_BOSS_KILL_REQUIREMENT

        self.stage = "normal"
        self.result_timer = 0

    def start_boss_intro(self):
        self.stage = "boss_intro"
        self.enemies.clear()
        self.clear_enemy_bullets()
        self.boss = Boss(self.boss_difficulty)

    def start_stage_clear(self):
        self.stage = "stage_clear"
        self.result_timer = 0
        self.clear_enemy_bullets()
        self.add_explosion(WIDTH // 2, 140, GOLD, count=120)

    def reset_for_next_stage(self):
        self.stage_number += 1

        # 小怪难度只轻微增加
        self.enemy_difficulty *= 1.08

        # Boss 难度魔鬼增加
        self.boss_difficulty *= 1.45

        self.kill_count = 0
        self.boss_kill_requirement = BASE_BOSS_KILL_REQUIREMENT + (self.stage_number - 1) * 5

        self.spawn_timer = 0
        self.result_timer = 0

        self.enemies.clear()
        self.ammos.clear()
        self.effects.clear()
        self.boss = None

        self.player.x = WIDTH // 2 - self.player.size // 2
        self.player.y = HEIGHT - 180
        self.player.alive = True
        self.player.invincible_timer = RESPAWN_INVINCIBLE_TIME
        self.player.respawn_timer = 0

        self.stage = "normal"

    def clear_enemy_bullets(self):
        self.ammos = [
            ammo for ammo in self.ammos
            if ammo.owner != "enemy"
        ]

    def add_explosion(self, x, y, color, count=36):
        for _ in range(count):
            self.effects.append(
                ExplosionParticle(x, y, color)
            )

    def player_death(self):
        if self.debug_mode:
            return

        if not self.player.is_vulnerable():
            return

        self.add_explosion(
            self.player.center_x(),
            self.player.center_y(),
            WHITE,
            count=60
        )

        self.lives -= 1
        self.clear_enemy_bullets()

        if self.lives <= 0:
            self.player.die()
            self.stage = "game_over"
        else:
            self.player.respawn()

    # -------------------------
    # 敌人生成
    # -------------------------

    def spawn_enemy(self):
        enemy_size = 66
        x = random.randint(0, WIDTH - enemy_size)
        y = -enemy_size

        self.enemies.append(
            Enemy(x, y, self.enemy_difficulty)
        )

    def update_spawn(self):
        if self.stage != "normal":
            return

        self.spawn_timer += 1

        spawn_interval = max(45, int(80 / self.enemy_difficulty))

        if self.spawn_timer >= spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

    # -------------------------
    # 碰撞检测
    # -------------------------

    def is_ammo_enemy_collision(self, ammo, enemy):
        return (
            ammo.x < enemy.x + enemy.size and
            ammo.x + ammo.width > enemy.x and
            ammo.y < enemy.y + enemy.size and
            ammo.y + ammo.height > enemy.y
        )

    def is_player_enemy_collision(self, player, enemy):
        circle_x = player.center_x()
        circle_y = player.center_y()
        radius = player.hitbox_radius

        nearest_x = max(enemy.x, min(circle_x, enemy.x + enemy.size))
        nearest_y = max(enemy.y, min(circle_y, enemy.y + enemy.size))

        dx = circle_x - nearest_x
        dy = circle_y - nearest_y

        return dx * dx + dy * dy <= radius * radius

    def is_ammo_player_collision(self, ammo, player):
        circle_x = player.center_x()
        circle_y = player.center_y()
        radius = player.hitbox_radius

        nearest_x = max(ammo.x, min(circle_x, ammo.x + ammo.width))
        nearest_y = max(ammo.y, min(circle_y, ammo.y + ammo.height))

        dx = circle_x - nearest_x
        dy = circle_y - nearest_y

        return dx * dx + dy * dy <= radius * radius

    def check_collisions(self):
        if self.stage == "game_over":
            return

        for ammo in self.ammos:
            if ammo.owner != "player" or not ammo.alive:
                continue

            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                if self.is_ammo_enemy_collision(ammo, enemy):
                    enemy_was_alive = enemy.alive
                    enemy.take_damage(ammo.damage)
                    ammo.alive = False

                    if enemy_was_alive and not enemy.alive:
                        self.kill_count += 1
                        self.score += int(ENEMY_SCORE * self.enemy_difficulty)
                        self.add_explosion(enemy.center_x(), enemy.center_y(), RED, count=36)

                    break

            if not ammo.alive:
                continue

            if self.boss is not None and self.boss.alive:
                if self.is_ammo_enemy_collision(ammo, self.boss):
                    result = self.boss.take_damage(ammo.damage)
                    ammo.alive = False

                    if result == "phase_clear":
                        self.score += int(BOSS_PHASE_SCORE * self.boss_difficulty)
                        self.clear_enemy_bullets()
                        self.add_explosion(self.boss.center_x(), self.boss.center_y(), PINK, count=80)

                    elif result == "dead":
                        self.score += int(BOSS_CLEAR_SCORE * self.boss_difficulty)
                        self.clear_enemy_bullets()
                        self.add_explosion(self.boss.center_x(), self.boss.center_y(), GOLD, count=160)
                        self.start_stage_clear()

        for ammo in self.ammos:
            if ammo.owner != "enemy" or not ammo.alive:
                continue

            if self.is_ammo_player_collision(ammo, self.player):
                ammo.alive = False
                self.player_death()

        for enemy in self.enemies:
            if enemy.alive and self.is_player_enemy_collision(self.player, enemy):
                self.player_death()

        if self.boss is not None and self.boss.alive:
            if self.is_player_enemy_collision(self.player, self.boss):
                self.player_death()

    # -------------------------
    # 更新
    # -------------------------

    def update(self):
        self.player.update()

        if self.stage == "normal":
            self.update_spawn()

            if self.kill_count >= self.boss_kill_requirement:
                self.start_boss_intro()

        elif self.stage == "boss_intro":
            if self.boss is not None:
                self.boss.update()

                if self.boss.active:
                    self.stage = "boss"

        elif self.stage == "boss":
            if self.boss is not None and self.boss.alive:
                self.boss.update()

                if self.boss.can_shoot():
                    new_ammos = self.boss.shoot(self.player)
                    self.ammos.extend(new_ammos)

        elif self.stage == "stage_clear":
            self.result_timer += 1

            if self.result_timer >= FPS * 4:
                self.reset_for_next_stage()

        for ammo in self.ammos:
            ammo.update()

        if self.stage == "normal":
            for enemy in self.enemies:
                enemy.update()

                if enemy.can_shoot():
                    new_ammos = enemy.shoot(self.player)
                    self.ammos.extend(new_ammos)

        for effect in self.effects:
            effect.update()

        self.check_collisions()

        self.ammos = [ammo for ammo in self.ammos if ammo.alive]
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        self.effects = [effect for effect in self.effects if effect.alive]

    # -------------------------
    # 绘制
    # -------------------------

    def draw_text(self, text, x, y, color=WHITE, small=False, big=False):
        if big:
            font = self.big_font
        elif small:
            font = self.small_font
        else:
            font = self.font

        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_boss_ui(self):
        if self.boss is None or not self.boss.alive:
            return

        self.draw_text(
            self.boss.current_phase_name(),
            20,
            20,
            WHITE,
            small=True
        )

        max_health = self.boss.phase_healths[self.boss.phase]
        ratio = max(0, self.boss.health / max_health)

        bar_x = 20
        bar_y = 48
        bar_w = WIDTH - 40
        bar_h = 12

        pygame.draw.rect(
            self.screen,
            WHITE,
            (bar_x, bar_y, bar_w, bar_h),
            1
        )

        pygame.draw.rect(
            self.screen,
            PINK,
            (bar_x, bar_y, int(bar_w * ratio), bar_h)
        )

    def draw_hud(self):
        self.draw_text(
            f"Score: {self.score}",
            20,
            HEIGHT - 116,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Lives: {self.lives}",
            20,
            HEIGHT - 92,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Stage: {self.stage_number}",
            20,
            HEIGHT - 68,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Enemy: {self.enemy_difficulty:.2f}  Boss: {self.boss_difficulty:.2f}",
            20,
            HEIGHT - 44,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Kills: {self.kill_count}/{self.boss_kill_requirement}",
            20,
            HEIGHT - 20,
            WHITE,
            small=True
        )

    def draw_stage_clear(self):
        self.draw_text(
            "STAGE CLEAR!",
            WIDTH // 2 - 160,
            HEIGHT // 2 - 100,
            GREEN,
            big=True
        )

        self.draw_text(
            f"Score: {self.score}",
            WIDTH // 2 - 90,
            HEIGHT // 2 - 35,
            WHITE
        )

        self.draw_text(
            f"Next Stage: {self.stage_number + 1}",
            WIDTH // 2 - 110,
            HEIGHT // 2 + 5,
            GOLD
        )

        self.draw_text(
            f"Enemy Difficulty: {self.enemy_difficulty * 1.08:.2f}",
            WIDTH // 2 - 150,
            HEIGHT // 2 + 45,
            WHITE
        )

        self.draw_text(
            f"Boss Difficulty: {self.boss_difficulty * 1.45:.2f}",
            WIDTH // 2 - 150,
            HEIGHT // 2 + 80,
            RED
        )

    def draw_game_over(self):
        self.draw_text(
            "GAME OVER",
            WIDTH // 2 - 140,
            HEIGHT // 2 - 80,
            RED,
            big=True
        )

        self.draw_text(
            f"Final Score: {self.score}",
            WIDTH // 2 - 120,
            HEIGHT // 2 - 20,
            WHITE
        )

        self.draw_text(
            "Press R to Restart",
            WIDTH // 2 - 120,
            HEIGHT // 2 + 30,
            GREEN
        )

        self.draw_text(
            "Press ESC to Quit",
            WIDTH // 2 - 110,
            HEIGHT // 2 + 70,
            WHITE
        )

    def draw(self):
        self.screen.fill(BLACK)

        if self.stage == "boss_intro":
            self.draw_text(
                "WARNING!!",
                WIDTH // 2 - 90,
                90,
                RED,
                big=True
            )

        self.player.draw(self.screen)

        for ammo in self.ammos:
            ammo.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.boss is not None and self.boss.alive:
            self.boss.draw(self.screen)
            self.draw_boss_ui()

        for effect in self.effects:
            effect.draw(self.screen)

        self.draw_hud()

        if self.stage == "stage_clear":
            self.draw_stage_clear()

        if self.stage == "game_over":
            self.draw_game_over()

        if self.debug_mode:
            self.draw_text(
                "DEBUG: INVINCIBLE",
                WIDTH - 210,
                20,
                GREEN,
                small=True
            )

        if self.debug_input_active:
            pygame.draw.rect(
                self.screen,
                WHITE,
                (WIDTH // 2 - 160, HEIGHT // 2 - 30, 320, 60),
                2
            )

            self.draw_text(
                "Enter Code: " + self.debug_text,
                WIDTH // 2 - 140,
                HEIGHT // 2 - 10,
                GREEN,
                small=True
            )

        pygame.display.flip()

    # -------------------------
    # 主循环
    # -------------------------

    def run(self):
        while self.running:
            self.handle_events()
            self.handle_input()
            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()


game = Game()
game.run()