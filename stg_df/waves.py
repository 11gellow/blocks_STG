import random

from .constants import HEIGHT, WIDTH
from .enemies import ENEMY_TYPES, attack_for_type


WAVE_GAP = 45


WAVE_PATTERNS = [
    {"name": "Twin top streams", "kind": "paired_stream", "type": 0, "count": 8, "delay": 12, "x": 130, "mirror_x": WIDTH - 130, "movement": "straight"},
    {"name": "Horizontal comb", "kind": "horizontal_line", "type": 1, "count": 9, "delay": 5, "y": -70, "movement": "straight"},
    {"name": "Right slash", "kind": "diagonal", "type": 2, "count": 8, "delay": 10, "side": "right", "movement": "straight"},
    {"name": "Left slash", "kind": "diagonal", "type": 3, "count": 8, "delay": 10, "side": "left", "movement": "straight"},
    {"name": "Mirrored scissors", "kind": "mirrored_diagonal", "type": 4, "count": 6, "delay": 14, "movement": "straight"},
    {"name": "Soft V", "kind": "v_formation", "type": 5, "count": 9, "delay": 4, "movement": "straight"},
    {"name": "Sine braid", "kind": "paired_stream", "type": 6, "count": 7, "delay": 13, "x": 170, "mirror_x": WIDTH - 170, "movement": "sine"},
    {"name": "Left hook", "kind": "side_sweep", "type": 7, "count": 7, "delay": 11, "side": "left", "movement": "curve"},
    {"name": "Right hook", "kind": "side_sweep", "type": 8, "count": 7, "delay": 11, "side": "right", "movement": "curve"},
    {"name": "Hover row", "kind": "horizontal_line", "type": 9, "count": 6, "delay": 7, "y": -80, "movement": "hover"},
    {"name": "Staggered lanes", "kind": "staggered_lanes", "type": 10, "count": 12, "delay": 8, "movement": "straight"},
    {"name": "Corner pincer", "kind": "corner_pincer", "type": 11, "count": 6, "delay": 16, "movement": "bezier"},
    {"name": "Arc drop", "kind": "arc", "type": 12, "count": 10, "delay": 5, "movement": "bezier"},
    {"name": "Checker rain", "kind": "checker", "type": 13, "count": 12, "delay": 6, "movement": "straight"},
    {"name": "Snake left", "kind": "snake", "type": 14, "count": 10, "delay": 9, "side": "left", "movement": "sine"},
    {"name": "Snake right", "kind": "snake", "type": 15, "count": 10, "delay": 9, "side": "right", "movement": "sine"},
    {"name": "Double columns", "kind": "columns", "type": 16, "count": 10, "delay": 8, "movement": "straight"},
    {"name": "Hourglass", "kind": "hourglass", "type": 17, "count": 12, "delay": 7, "movement": "bezier"},
    {"name": "Falling cross", "kind": "falling_cross", "type": 18, "count": 9, "delay": 5, "movement": "straight"},
    {"name": "Wedge left", "kind": "wedge", "type": 19, "count": 10, "delay": 6, "side": "left", "movement": "straight"},
    {"name": "Wedge right", "kind": "wedge", "type": 20, "count": 10, "delay": 6, "side": "right", "movement": "straight"},
    {"name": "Top curtain", "kind": "curtain_rows", "type": 21, "count": 15, "delay": 4, "movement": "hover"},
    {"name": "Delayed pairs", "kind": "delayed_pairs", "type": 22, "count": 8, "delay": 18, "movement": "straight"},
    {"name": "Rising side ambush", "kind": "side_ambush", "type": 23, "count": 8, "delay": 10, "movement": "curve"},
    {"name": "Wide S sweep", "kind": "horizontal_line", "type": 24, "count": 7, "delay": 7, "y": -70, "movement": "sine"},
    {"name": "Comb left", "kind": "comb", "type": 25, "count": 10, "delay": 6, "side": "left", "movement": "straight"},
    {"name": "Comb right", "kind": "comb", "type": 26, "count": 10, "delay": 6, "side": "right", "movement": "straight"},
    {"name": "Zigzag row", "kind": "horizontal_line", "type": 27, "count": 8, "delay": 6, "y": -70, "movement": "zigzag"},
    {"name": "Inverted stairs", "kind": "stairs", "type": 28, "count": 10, "delay": 8, "side": "right", "movement": "straight"},
    {"name": "Stairs", "kind": "stairs", "type": 29, "count": 10, "delay": 8, "side": "left", "movement": "straight"},
    {"name": "Center blossom", "kind": "center_burst", "type": 30, "count": 9, "delay": 5, "movement": "bezier"},
    {"name": "Double V", "kind": "double_v", "type": 31, "count": 12, "delay": 4, "movement": "straight"},
    {"name": "Braid crossing", "kind": "braid_cross", "type": 32, "count": 12, "delay": 9, "movement": "sine"},
    {"name": "Spiral entry", "kind": "spiral_entry", "type": 33, "count": 12, "delay": 7, "movement": "bezier"},
    {"name": "Wide waterfall", "kind": "waterfall", "type": 34, "count": 16, "delay": 5, "movement": "straight"},
    {"name": "Final mixed gate", "kind": "mixed_gate", "type": 35, "count": 18, "delay": 5, "movement": "bezier"},
]


class WaveDirector:
    def __init__(self):
        self.wave_index = 0
        self.timer = 0
        self.queue = []
        self.current_patterns = []

    def reset(self, wave_index=0):
        self.wave_index = wave_index
        self.timer = 0
        self.queue = []
        self.current_patterns = []

    def update(self):
        self.timer += 1
        ready = []
        remaining = []

        for event in self.queue:
            if event["time"] <= self.timer:
                ready.append(event)
            else:
                remaining.append(event)

        self.queue = remaining
        return ready

    def start_next_wave(self, difficulty, stage_number, stage_wave_number):
        selection = choose_wave_patterns(self.wave_index, stage_number, stage_wave_number)
        count_scale = 0.62 if len(selection) == 2 else 0.82
        queue = []

        for component_index, pattern_index in enumerate(selection):
            pattern = dict(WAVE_PATTERNS[pattern_index])
            pattern["delay"] = max(8, pattern["delay"])
            events = build_wave(
                pattern,
                self.wave_index,
                difficulty,
                count_scale=count_scale,
                time_offset=component_index * 18,
            )
            queue.extend(events)

        self.queue = sorted(queue, key=lambda event: event["time"])
        self.current_patterns = selection
        self.timer = 0
        self.wave_index += 1

    def is_spawning(self):
        return bool(self.queue)


def choose_wave_patterns(wave_index, stage_number, stage_wave_number):
    rng = random.Random(0x5EED + stage_number * 101 + stage_wave_number * 17 + wave_index * 37)
    first = rng.randrange(len(WAVE_PATTERNS))

    if stage_wave_number in (2, 4):
        second = rng.randrange(len(WAVE_PATTERNS))
        while second == first:
            second = rng.randrange(len(WAVE_PATTERNS))
        return [first, second]

    return [first]


def build_wave(pattern, wave_index, difficulty, count_scale=1.0, time_offset=0):
    kind = pattern["kind"]
    enemy_type = pattern["type"] % len(ENEMY_TYPES)
    count = max(4, int(pattern["count"] * count_scale))
    delay = max(8, pattern["delay"])
    movement_name = pattern.get("movement", "straight")

    events = []

    def add(time, x, y, movement, local_type=enemy_type):
        events.append({
            "time": time,
            "x": x,
            "y": y,
            "enemy_type": local_type % len(ENEMY_TYPES),
            "attack": attack_for_type(local_type, wave_index // len(WAVE_PATTERNS)),
            "movement": movement,
            "shot_phase": (time + time_offset + local_type * 11) % 70,
        })

    if kind == "paired_stream":
        for i in range(count):
            y = -80 - i * 6
            add(time_offset + i * delay, pattern["x"], y, make_movement(movement_name, 0.35, 1.25, phase=i * 0.4))
            add(time_offset + i * delay, pattern["mirror_x"], y, make_movement(movement_name, -0.35, 1.25, phase=3.14 + i * 0.4))

    elif kind == "horizontal_line":
        spacing = WIDTH / (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            add(time_offset + i * delay, x, pattern.get("y", -70), make_movement(movement_name, 0, 1.15, phase=i * 0.55, target_y=130 + i % 3 * 28))

    elif kind == "diagonal":
        right = pattern.get("side") == "right"
        for i in range(count):
            x = WIDTH + 40 if right else -80
            y = -80 - i * 18
            vx = -1.85 if right else 1.85
            add(time_offset + i * delay, x, y, make_movement("straight", vx, 1.35))

    elif kind == "mirrored_diagonal":
        for i in range(count):
            y = -90 - i * 20
            add(time_offset + i * delay, -80, y, make_movement("straight", 1.55, 1.25))
            add(time_offset + i * delay, WIDTH + 40, y, make_movement("straight", -1.55, 1.25))

    elif kind == "v_formation":
        center = count // 2
        for i in range(count):
            offset = i - center
            x = WIDTH / 2 + offset * 48
            y = -70 - abs(offset) * 22
            add(time_offset + i * delay, x, y, make_movement(movement_name, offset * 0.06, 1.2))

    elif kind == "side_sweep":
        left = pattern.get("side") == "left"
        for i in range(count):
            x = -80 if left else WIDTH + 30
            y = 40 + i * 30
            vx = 2.2 if left else -2.2
            curve = -0.010 if left else 0.010
            add(time_offset + i * delay, x, y, make_movement("curve", vx, 0.75, curve=curve))

    elif kind == "staggered_lanes":
        lanes = [95, 185, 275, 365, 455, 545]
        for i in range(count):
            x = lanes[i % len(lanes)]
            y = -90 - (i // len(lanes)) * 80
            add(time_offset + i * delay, x, y, make_movement("straight", 0, 1.35))

    elif kind == "corner_pincer":
        for i in range(count):
            add(time_offset + i * delay, -70, -80 - i * 8, make_movement("bezier", 0, 1.0, cx=WIDTH * 0.28, cy=180, ex=WIDTH * 0.48, ey=HEIGHT + 80))
            add(time_offset + i * delay, WIDTH + 20, -80 - i * 8, make_movement("bezier", 0, 1.0, cx=WIDTH * 0.72, cy=180, ex=WIDTH * 0.52, ey=HEIGHT + 80))

    elif kind == "arc":
        spacing = WIDTH / (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            peak = 120 + abs(i - count / 2) * 18
            add(time_offset + i * delay, x, -90, make_movement("bezier", 0, 1.0, cx=WIDTH / 2, cy=peak, ex=WIDTH - x, ey=HEIGHT + 90))

    elif kind == "checker":
        for i in range(count):
            row = i // 4
            col = i % 4
            x = 110 + col * 150 + (row % 2) * 55
            y = -90 - row * 80
            add(time_offset + i * delay, x, y, make_movement("straight", 0, 1.2 + row * 0.08))

    elif kind == "snake":
        left = pattern.get("side") == "left"
        x = 120 if left else WIDTH - 120
        vx = 0.45 if left else -0.45
        for i in range(count):
            add(time_offset + i * delay, x, -80 - i * 12, make_movement("sine", vx, 1.2, amp=105, freq=0.055, phase=i * 0.85))

    elif kind == "columns":
        columns = [155, WIDTH - 155]
        for i in range(count):
            x = columns[i % 2]
            y = -80 - (i // 2) * 48
            add(time_offset + i * delay, x, y, make_movement("straight", 0.18 if i % 2 == 0 else -0.18, 1.3))

    elif kind == "hourglass":
        for i in range(count):
            left = i % 2 == 0
            x = -70 if left else WIDTH + 20
            ex = WIDTH + 40 if left else -90
            cx = WIDTH * (0.44 if left else 0.56)
            add(time_offset + i * delay, x, -70 - i * 10, make_movement("bezier", 0, 1.0, cx=cx, cy=HEIGHT * 0.32, ex=ex, ey=HEIGHT + 80))

    elif kind == "falling_cross":
        center = WIDTH / 2
        for i in range(count):
            offset = (i - count // 2) * 45
            add(time_offset + i * delay, center + offset, -70, make_movement("straight", 0, 1.35))
            if i % 2 == 0:
                add(time_offset + i * delay, center, -70 - abs(offset), make_movement("straight", offset * 0.01, 1.1))

    elif kind == "wedge":
        left = pattern.get("side") == "left"
        for i in range(count):
            row = i // 3
            col = i % 3
            x = (70 + col * 55 + row * 38) if left else (WIDTH - 120 - col * 55 - row * 38)
            y = -70 - row * 48
            add(time_offset + i * delay, x, y, make_movement("straight", 0.35 if left else -0.35, 1.25))

    elif kind == "curtain_rows":
        for i in range(count):
            row = i // 5
            col = i % 5
            x = 95 + col * 125
            y = -80 - row * 52
            add(time_offset + i * delay, x, y, make_movement("hover", 0, 1.45, target_y=115 + row * 42, drift=(col - 2) * 0.08))

    elif kind == "delayed_pairs":
        for i in range(count):
            x = 120 + (i % 4) * 150
            y = -80 - (i // 4) * 80
            add(time_offset + i * delay, x, y, make_movement("straight", -0.55, 1.2))
            add(time_offset + i * delay + 24, WIDTH - x, y - 20, make_movement("straight", 0.55, 1.2))

    elif kind == "side_ambush":
        for i in range(count):
            top = i % 2 == 0
            x = -80 if top else WIDTH + 30
            y = 70 + i * 34
            vx = 2.15 if top else -2.15
            add(time_offset + i * delay, x, y, make_movement("curve", vx, 0.25, curve=-0.006 if top else 0.006))

    elif kind == "comb":
        left = pattern.get("side") == "left"
        for i in range(count):
            x = -70 if left else WIDTH + 20
            y = -60 + i * 42
            vx = 1.9 if left else -1.9
            add(time_offset + i * delay, x, y, make_movement("straight", vx, 0.85))

    elif kind == "stairs":
        left = pattern.get("side") == "left"
        for i in range(count):
            x = 70 + i * 52 if left else WIDTH - 110 - i * 52
            y = -60 - i * 16
            add(time_offset + i * delay, x, y, make_movement("straight", 0, 1.32))

    elif kind == "center_burst":
        for i in range(count):
            angle = 360 * i / count
            start_x = WIDTH / 2 + math_cos(angle) * 260
            start_y = -95
            add(time_offset + i * delay, start_x, start_y, make_movement("bezier", 0, 1.0, cx=WIDTH / 2, cy=150, ex=WIDTH / 2 + math_cos(angle + 180) * 260, ey=HEIGHT + 70))

    elif kind == "double_v":
        center = count // 2
        for i in range(count):
            offset = i - center
            x = WIDTH / 2 + offset * 38
            y = -80 - abs(offset) * 18
            vx = -0.25 if offset < 0 else 0.25
            add(time_offset + i * delay, x, y, make_movement("straight", vx, 1.25))
            if i % 3 == 0:
                add(time_offset + i * delay + 18, WIDTH - x, y - 20, make_movement("straight", -vx, 1.2), enemy_type + 1)

    elif kind == "braid_cross":
        for i in range(count):
            left_x = 120
            right_x = WIDTH - 120
            add(time_offset + i * delay, left_x, -80 - i * 8, make_movement("sine", 0.75, 1.15, amp=95, freq=0.05, phase=i * 0.6))
            add(time_offset + i * delay, right_x, -80 - i * 8, make_movement("sine", -0.75, 1.15, amp=95, freq=0.05, phase=3.14 + i * 0.6))

    elif kind == "spiral_entry":
        for i in range(count):
            angle = i * 32
            x = WIDTH / 2 + math_cos(angle) * (90 + i * 8)
            cx = WIDTH / 2 + math_cos(angle + 90) * 220
            ex = WIDTH / 2 + math_cos(angle + 180) * 250
            add(time_offset + i * delay, x, -90, make_movement("bezier", 0, 1.0, cx=cx, cy=160 + i * 5, ex=ex, ey=HEIGHT + 80))

    elif kind == "waterfall":
        for i in range(count):
            x = 60 + (i * 87) % (WIDTH - 120)
            y = -70 - (i // 6) * 55
            add(time_offset + i * delay, x, y, make_movement("straight", ((i % 3) - 1) * 0.25, 1.38))

    elif kind == "mixed_gate":
        for i in range(count):
            local_type = enemy_type if i % 3 else enemy_type - 1
            left = i % 2 == 0
            x = -70 if left else WIDTH + 20
            cx = WIDTH * (0.32 if left else 0.68)
            ex = WIDTH * (0.68 if left else 0.32)
            add(time_offset + i * delay, x, -80 - i * 6, make_movement("bezier", 0, 1.0, cx=cx, cy=140 + i * 4, ex=ex, ey=HEIGHT + 80), local_type)

    return sorted(events, key=lambda event: event["time"])


def make_movement(kind, vx=0, vy=1.2, **kwargs):
    movement = {"kind": kind, "vx": vx, "vy": vy}
    movement.update(kwargs)
    return movement


def math_cos(angle_degree):
    import math

    return math.cos(math.radians(angle_degree))

