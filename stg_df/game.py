import os
import math
import sys

import pygame

from .boss import Boss
from .constants import (
    BLACK,
    BOSS_CLEAR_SCORE,
    BOSS_PHASE_SCORE,
    ENEMY_SCORE,
    FPS,
    GOLD,
    GREEN,
    HEIGHT,
    INITIAL_LIVES,
    PINK,
    RED,
    RESPAWN_INVINCIBLE_TIME,
    STAGE_BONUS_BASE,
    STAGE_RESULT_TIME,
    TOTAL_STAGES,
    WAVES_PER_STAGE,
    WHITE,
    WIDTH,
)
from .effects import ExplosionParticle
from .enemies import Enemy
from .player import Player
from .waves import WaveDirector


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        pygame.mixer.init()

        music_path = resource_path("badapple.mp3")
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
        self.wave_director = WaveDirector()

        self.score = 0
        self.lives = INITIAL_LIVES
        self.stage_number = 1
        self.stage_start_score = 0
        self.current_stage_wave = 0
        self.wave_active = False
        self.wave_pause_timer = FPS

        # 拆成两套难度：
        # 小怪难度温和增长
        # Boss 难度魔鬼增长
        self.enemy_difficulty = 1.0
        self.boss_difficulty = 1.0

        self.kill_count = 0
        self.stage_kill_count = 0

        self.stage = "normal"
        self.result_timer = 0
        self.result_base_score = 0
        self.result_stage_score = 0
        self.result_bonus = 0

        self.debug_mode = False
        self.debug_input_active = False
        self.debug_text = ""

        self.running = True

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

                elif self.stage in ("game_over", "game_clear"):
                    if event.key == pygame.K_r:
                        self.restart_game()

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    # -------------------------
    # 输入处理
    # -------------------------

    def handle_input(self):
        if self.stage in ("game_over", "game_clear", "stage_finished"):
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
        self.wave_director.reset()

        self.score = 0
        self.lives = INITIAL_LIVES
        self.stage_number = 1
        self.stage_start_score = 0
        self.current_stage_wave = 0
        self.wave_active = False
        self.wave_pause_timer = FPS

        self.enemy_difficulty = 1.0
        self.boss_difficulty = 1.0

        self.kill_count = 0
        self.stage_kill_count = 0

        self.stage = "normal"
        self.result_timer = 0
        self.result_base_score = 0
        self.result_stage_score = 0
        self.result_bonus = 0

    def start_boss_intro(self):
        self.stage = "boss_intro"
        self.enemies.clear()
        self.clear_enemy_bullets()
        self.wave_director.reset()
        self.boss = Boss(self.boss_difficulty)

    def start_stage_finished(self):
        self.stage = "stage_finished"
        self.result_timer = 0
        self.result_base_score = self.score
        self.result_stage_score = self.score - self.stage_start_score
        self.result_bonus = (
            STAGE_BONUS_BASE * self.stage_number
            + self.lives * 5000
            + self.stage_kill_count * 800
        )
        self.add_explosion(WIDTH // 2, 150, GOLD, count=90)

    def start_game_clear(self):
        self.stage = "game_clear"
        self.result_timer = 0
        self.clear_enemy_bullets()
        self.add_explosion(WIDTH // 2, 180, GOLD, count=180)

    def reset_for_next_stage(self):
        self.stage_number += 1

        # 小怪难度只轻微增加
        self.enemy_difficulty *= 1.08

        # Boss 难度魔鬼增加
        self.boss_difficulty *= 1.45

        self.stage_start_score = self.score
        self.current_stage_wave = 0
        self.wave_active = False
        self.wave_pause_timer = FPS
        self.stage_kill_count = 0

        self.result_timer = 0
        self.wave_director.reset()

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

    def spawn_enemy(self, event):
        self.enemies.append(
            Enemy(
                event["x"],
                event["y"],
                self.enemy_difficulty,
                enemy_type=event["enemy_type"],
                attack_pattern=event["attack"],
                movement=event["movement"],
                shot_phase=event["shot_phase"],
            )
        )

    def update_spawn(self):
        if self.stage != "normal":
            return

        if not self.wave_active:
            if self.wave_pause_timer > 0:
                self.wave_pause_timer -= 1
                return

            if self.current_stage_wave < WAVES_PER_STAGE:
                self.current_stage_wave += 1
                self.wave_active = True
                self.wave_director.start_next_wave(
                    self.enemy_difficulty,
                    self.stage_number,
                    self.current_stage_wave,
                )

        for event in self.wave_director.update():
            self.spawn_enemy(event)

    def enemy_bullets_alive(self):
        return any(ammo.owner == "enemy" and ammo.alive for ammo in self.ammos)

    def update_wave_completion(self):
        if self.stage != "normal" or not self.wave_active:
            return

        if self.wave_director.is_spawning() or self.enemies or self.enemy_bullets_alive():
            return

        if self.current_stage_wave >= WAVES_PER_STAGE:
            self.wave_active = False
            self.start_stage_finished()
        else:
            self.wave_active = False
            self.wave_pause_timer = FPS

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

        segment = ammo.collision_segment()
        if segment is not None:
            start, end = segment
            distance = self.distance_point_to_segment(circle_x, circle_y, start, end)
            return distance <= radius + ammo.player_collision_radius()

        if ammo.owner == "enemy":
            dx = circle_x - ammo.x
            dy = circle_y - ammo.y
            hit_radius = radius + ammo.player_collision_radius()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        nearest_x = max(ammo.x, min(circle_x, ammo.x + ammo.width))
        nearest_y = max(ammo.y, min(circle_y, ammo.y + ammo.height))

        dx = circle_x - nearest_x
        dy = circle_y - nearest_y

        ammo_radius = ammo.player_collision_radius()
        return dx * dx + dy * dy <= (radius + ammo_radius) * (radius + ammo_radius)

    def distance_point_to_segment(self, px, py, start, end):
        sx, sy = start
        ex, ey = end
        dx = ex - sx
        dy = ey - sy

        if dx == 0 and dy == 0:
            return math.hypot(px - sx, py - sy)

        t = ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        nearest_x = sx + t * dx
        nearest_y = sy + t * dy
        return math.hypot(px - nearest_x, py - nearest_y)

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
                        self.stage_kill_count += 1
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
                        self.start_game_clear()

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

        elif self.stage == "stage_finished":
            self.result_timer += 1
            progress = min(1, self.result_timer / (FPS * 2.4))
            eased = 1 - (1 - progress) * (1 - progress)
            self.score = self.result_base_score + int(self.result_bonus * eased)

            if self.result_timer >= STAGE_RESULT_TIME:
                self.score = self.result_base_score + self.result_bonus

                if self.stage_number >= TOTAL_STAGES:
                    self.start_boss_intro()
                else:
                    self.reset_for_next_stage()

        elif self.stage == "game_clear":
            self.result_timer += 1

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

        self.update_wave_completion()

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

    def draw_centered_text(self, text, y, color=WHITE, small=False, big=False):
        if big:
            font = self.big_font
        elif small:
            font = self.small_font
        else:
            font = self.font

        surface = font.render(text, True, color)
        x = WIDTH // 2 - surface.get_width() // 2
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
            f"Stage: {self.stage_number}/{TOTAL_STAGES}",
            20,
            HEIGHT - 68,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Wave: {self.current_stage_wave}/{WAVES_PER_STAGE}",
            20,
            HEIGHT - 44,
            WHITE,
            small=True
        )

        self.draw_text(
            f"Enemy: {self.enemy_difficulty:.2f}  Boss: {self.boss_difficulty:.2f}",
            20,
            HEIGHT - 20,
            WHITE,
            small=True
        )

    def draw_stage_finished(self):
        flash_colors = [WHITE, GOLD, GREEN, WHITE]
        color = flash_colors[(self.result_timer // 5) % len(flash_colors)]
        y = 145 + ((self.result_timer // 4) % 2)

        self.draw_centered_text("STAGE FINISHED", y + 4, RED, big=True)
        self.draw_centered_text("STAGE FINISHED", y, color, big=True)

        progress = min(1, self.result_timer / (FPS * 2.4))
        shown_bonus = int(self.result_bonus * (1 - (1 - progress) * (1 - progress)))
        life_bonus = self.lives * 5000
        enemy_bonus = self.stage_kill_count * 800
        clear_bonus = STAGE_BONUS_BASE * self.stage_number
        rows = [
            ("Stage Score", self.result_stage_score, 70),
            ("Clear Bonus", clear_bonus, 105),
            ("Life Bonus", life_bonus, 140),
            ("Enemy Bonus", enemy_bonus, 175),
            ("Bonus Total", shown_bonus, 225),
            ("Total Score", self.score, 270),
        ]

        panel_x = 125
        panel_y = 270
        panel_w = WIDTH - panel_x * 2
        pygame.draw.rect(self.screen, (20, 20, 28), (panel_x, panel_y, panel_w, 330))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_w, 330), 1)

        for label, value, offset_y in rows:
            if self.result_timer < offset_y:
                continue

            row_y = panel_y + 35 + (offset_y - 70) // 35 * 38
            self.draw_text(label, panel_x + 32, row_y, WHITE)
            value_text = f"{value:>8}"
            self.draw_text(value_text, panel_x + panel_w - 150, row_y, GOLD)

        if self.result_timer > FPS * 3:
            next_text = "Boss Approaching" if self.stage_number >= TOTAL_STAGES else f"Next Stage: {self.stage_number + 1}"
            self.draw_centered_text(next_text, panel_y + 285, GREEN)

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

    def draw_game_clear(self):
        flash_colors = [GOLD, WHITE, GREEN, WHITE]
        color = flash_colors[(self.result_timer // 6) % len(flash_colors)]

        self.draw_centered_text("ALL CLEAR", HEIGHT // 2 - 100, color, big=True)
        self.draw_centered_text(f"Final Score: {self.score}", HEIGHT // 2 - 30, WHITE)
        self.draw_centered_text("Press R to Restart", HEIGHT // 2 + 35, GREEN)
        self.draw_centered_text("Press ESC to Quit", HEIGHT // 2 + 75, WHITE)

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

        if self.stage == "stage_finished":
            self.draw_stage_finished()

        if self.stage == "game_over":
            self.draw_game_over()

        if self.stage == "game_clear":
            self.draw_game_clear()

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


