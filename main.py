import array
import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional

import pygame

WIDTH, HEIGHT = 960, 540
GROUND_Y = HEIGHT - 120
GRAVITY = 2200


class GameMode(Enum):
    RUNNING = auto()
    VICTORY = auto()
    DEFEAT = auto()


@dataclass
class AttackData:
    damage: int
    stamina_cost: int
    duration: float
    cooldown: float
    hitbox_width: int
    knockback: float
    active_start: float
    active_end: float


LIGHT_ATTACK = AttackData(
    damage=12,
    stamina_cost=12,
    duration=0.24,
    cooldown=0.35,
    hitbox_width=70,
    knockback=220,
    active_start=0.08,
    active_end=0.18,
)

HEAVY_ATTACK = AttackData(
    damage=24,
    stamina_cost=24,
    duration=0.42,
    cooldown=0.62,
    hitbox_width=96,
    knockback=340,
    active_start=0.12,
    active_end=0.28,
)

PARRY_COST = 16
PARRY_WINDOW = 0.25
PARRY_COOLDOWN = 0.6

STAMINA_REGEN = 26  # per second


@dataclass
class Animation:
    frames: List[pygame.Surface]
    frame_durations: List[float]
    loop: bool = True


class AnimatedSprite:
    def __init__(self, animations: Dict[str, Animation], default: str):
        self.animations = animations
        self.current = default
        self.time = 0.0
        self.frame_index = 0
        self.flip = False

    def play(self, name: str, force: bool = False):
        if self.current != name or force:
            self.current = name
            self.time = 0.0
            self.frame_index = 0

    def set_flip(self, flip: bool):
        self.flip = flip

    def update(self, dt: float):
        animation = self.animations[self.current]
        if not animation.frames:
            return
        self.time += dt
        while self.time >= animation.frame_durations[self.frame_index]:
            self.time -= animation.frame_durations[self.frame_index]
            self.frame_index += 1
            if self.frame_index >= len(animation.frames):
                if animation.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(animation.frames) - 1
                    break

    def get_frame(self) -> pygame.Surface:
        frame = self.animations[self.current].frames[self.frame_index]
        if self.flip:
            return pygame.transform.flip(frame, True, False)
        return frame


@dataclass
class TrailSegment:
    rect: pygame.Rect
    color: pygame.Color
    life: float


def _lerp_color(a: pygame.Color, b: pygame.Color, t: float) -> pygame.Color:
    t = max(0.0, min(1.0, t))
    return pygame.Color(
        int(a.r + (b.r - a.r) * t),
        int(a.g + (b.g - a.g) * t),
        int(a.b + (b.b - a.b) * t),
    )


def _create_aura_surface(size: int, color: pygame.Color, strength: float) -> pygame.Surface:
    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    for radius in range(size, 0, -1):
        alpha = int(120 * (radius / size) ** strength)
        pygame.draw.circle(surface, (color.r, color.g, color.b, alpha), (size, size), radius)
    return surface


def _create_player_frames() -> Dict[str, Animation]:
    body_color = pygame.Color(25, 45, 110)
    edge_color = pygame.Color(140, 220, 255)
    aura_color = pygame.Color(90, 140, 255)

    def base_pose(lean: float = 0.0, aura_scale: float = 1.0, blade: bool = False) -> pygame.Surface:
        surf = pygame.Surface((96, 120), pygame.SRCALPHA)
        aura = _create_aura_surface(46, aura_color, 1.6)
        aura_width = max(4, int(aura.get_width() * aura_scale))
        aura_height = max(4, int(aura.get_height() * aura_scale))
        aura = pygame.transform.smoothscale(aura, (aura_width, aura_height))
        surf.blit(aura, (48 - aura.get_width() // 2 + int(lean * 2), 44 - aura.get_height() // 2))

        torso = pygame.Rect(36 + int(lean * 6), 42, 28, 52)
        pygame.draw.rect(surf, body_color, torso, border_radius=10)
        pygame.draw.rect(surf, edge_color, torso.inflate(6, 6), 3, border_radius=16)

        head_center = (torso.centerx, 32)
        pygame.draw.circle(surf, edge_color, head_center, 14, width=3)
        pygame.draw.circle(surf, pygame.Color(10, 20, 50), head_center, 13)

        leg_left = pygame.Rect(torso.left + 1, torso.bottom - 2, 10, 32)
        leg_right = pygame.Rect(torso.right - 11, torso.bottom - 2, 10, 32)
        pygame.draw.rect(surf, body_color, leg_left, border_radius=6)
        pygame.draw.rect(surf, body_color, leg_right, border_radius=6)
        pygame.draw.rect(surf, edge_color, leg_left.inflate(4, 4), 2, border_radius=6)
        pygame.draw.rect(surf, edge_color, leg_right.inflate(4, 4), 2, border_radius=6)

        arm_length = 42
        arm_width = 10
        arm_offset = int(lean * 10)
        pygame.draw.rect(
            surf,
            body_color,
            (torso.centerx + arm_offset - arm_width // 2, torso.y + 6, arm_width, arm_length),
            border_radius=6,
        )
        pygame.draw.rect(
            surf,
            edge_color,
            (torso.centerx + arm_offset - arm_width // 2, torso.y + 6, arm_width, arm_length),
            2,
            border_radius=6,
        )

        if blade:
            blade_rect = pygame.Rect(torso.centerx + arm_offset + 6, torso.y + 12, 12, 58)
            pygame.draw.rect(surf, pygame.Color(180, 240, 255), blade_rect, border_radius=6)
            pygame.draw.rect(surf, pygame.Color(90, 150, 255), blade_rect.inflate(2, 2), 2, border_radius=6)

        return surf

    idle_frames = [
        base_pose(lean=0.0, aura_scale=1.0),
        base_pose(lean=0.03, aura_scale=1.1),
    ]
    run_frames = [
        base_pose(lean=-0.3, aura_scale=0.9),
        base_pose(lean=-0.15, aura_scale=1.05),
        base_pose(lean=0.15, aura_scale=1.1),
        base_pose(lean=0.3, aura_scale=0.95),
    ]
    jump_frame = base_pose(lean=0.05, aura_scale=1.2)
    crouch_frame = pygame.transform.smoothscale(base_pose(lean=0.0, aura_scale=0.9), (96, 96))

    light_frames = [base_pose(lean=-0.2, aura_scale=1.0, blade=True), base_pose(lean=0.25, aura_scale=1.15, blade=True)]
    heavy_frames = [
        base_pose(lean=-0.35, aura_scale=0.95, blade=True),
        base_pose(lean=0.4, aura_scale=1.2, blade=True),
        base_pose(lean=0.2, aura_scale=1.25, blade=True),
    ]
    parry_frames = [
        base_pose(lean=0.0, aura_scale=1.35),
        base_pose(lean=0.0, aura_scale=1.5),
    ]
    hit_frame = pygame.transform.smoothscale(base_pose(lean=-0.1, aura_scale=0.8), (100, 110))

    return {
        "idle": Animation(idle_frames, [0.28, 0.32]),
        "run": Animation(run_frames, [0.08, 0.08, 0.08, 0.08]),
        "jump": Animation([jump_frame], [0.2], loop=False),
        "crouch": Animation([crouch_frame], [0.2], loop=False),
        "light": Animation(light_frames, [0.12, 0.12], loop=False),
        "heavy": Animation(heavy_frames, [0.1, 0.12, 0.14], loop=False),
        "parry": Animation(parry_frames, [0.1, 0.1], loop=False),
        "hit": Animation([hit_frame], [0.3], loop=False),
    }


def _create_enemy_frames() -> Dict[str, Animation]:
    body_color = pygame.Color(50, 10, 70)
    edge_color = pygame.Color(220, 150, 255)
    aura_color = pygame.Color(180, 90, 255)

    def base_pose(lean: float = 0.0, aura_scale: float = 1.0, blade: bool = False) -> pygame.Surface:
        surf = pygame.Surface((104, 126), pygame.SRCALPHA)
        aura = _create_aura_surface(48, aura_color, 1.8)
        aura_width = max(4, int(aura.get_width() * aura_scale))
        aura_height = max(4, int(aura.get_height() * aura_scale))
        aura = pygame.transform.smoothscale(aura, (aura_width, aura_height))
        surf.blit(aura, (52 - aura.get_width() // 2 + int(lean * 3), 48 - aura.get_height() // 2))

        torso = pygame.Rect(38 + int(lean * 8), 44, 30, 60)
        pygame.draw.rect(surf, body_color, torso, border_radius=12)
        pygame.draw.rect(surf, edge_color, torso.inflate(6, 6), 3, border_radius=18)

        head_center = (torso.centerx, 30)
        pygame.draw.circle(surf, edge_color, head_center, 16, width=4)
        pygame.draw.circle(surf, pygame.Color(25, 5, 40), head_center, 15)

        leg_left = pygame.Rect(torso.left + 2, torso.bottom - 4, 12, 36)
        leg_right = pygame.Rect(torso.right - 14, torso.bottom - 4, 12, 36)
        pygame.draw.rect(surf, body_color, leg_left, border_radius=6)
        pygame.draw.rect(surf, body_color, leg_right, border_radius=6)
        pygame.draw.rect(surf, edge_color, leg_left.inflate(6, 6), 2, border_radius=8)
        pygame.draw.rect(surf, edge_color, leg_right.inflate(6, 6), 2, border_radius=8)

        arm_width = 12
        pygame.draw.rect(
            surf,
            body_color,
            (torso.centerx - arm_width // 2 + int(lean * 14), torso.y + 6, arm_width, 48),
            border_radius=6,
        )
        pygame.draw.rect(
            surf,
            edge_color,
            (torso.centerx - arm_width // 2 + int(lean * 14), torso.y + 6, arm_width, 48),
            2,
            border_radius=6,
        )

        if blade:
            scythe_rect = pygame.Rect(torso.centerx + int(lean * 18), torso.y - 6, 16, 68)
            pygame.draw.rect(surf, pygame.Color(240, 180, 255), scythe_rect, border_radius=8)
            pygame.draw.rect(surf, pygame.Color(120, 40, 200), scythe_rect.inflate(4, 4), 2, border_radius=10)

        return surf

    idle = [base_pose(lean=0.0, aura_scale=1.0), base_pose(lean=-0.05, aura_scale=1.1)]
    patrol = [
        base_pose(lean=-0.25, aura_scale=0.95),
        base_pose(lean=-0.1, aura_scale=1.05),
        base_pose(lean=0.15, aura_scale=1.1),
        base_pose(lean=0.3, aura_scale=0.9),
    ]
    windup = [base_pose(lean=-0.4, aura_scale=0.85, blade=True)]
    attack = [
        base_pose(lean=-0.3, aura_scale=0.9, blade=True),
        base_pose(lean=0.35, aura_scale=1.25, blade=True),
        base_pose(lean=0.2, aura_scale=1.4, blade=True),
    ]
    stunned = [base_pose(lean=-0.2, aura_scale=0.7)]

    return {
        "idle": Animation(idle, [0.32, 0.32]),
        "move": Animation(patrol, [0.1, 0.1, 0.1, 0.1]),
        "windup": Animation(windup, [0.3], loop=False),
        "attack": Animation(attack, [0.08, 0.12, 0.14], loop=False),
        "stunned": Animation(stunned, [0.4], loop=False),
        "hit": Animation([pygame.transform.smoothscale(base_pose(lean=-0.25, aura_scale=0.75), (110, 120))], [0.25], loop=False),
    }


def _create_player_animator() -> AnimatedSprite:
    return AnimatedSprite(_create_player_frames(), "idle")


def _create_enemy_animator() -> AnimatedSprite:
    return AnimatedSprite(_create_enemy_frames(), "idle")


class Player:
    def __init__(self, x: float):
        self.rect = pygame.Rect(x, GROUND_Y - 90, 54, 90)
        self.velocity = pygame.Vector2(0, 0)
        self.max_health = 100
        self.health = self.max_health
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.facing = 1
        self.crouching = False
        self.on_ground = True

        self.attack_timer = 0.0
        self.attack_cooldown = 0.0
        self.current_attack: Optional[AttackData] = None
        self.attack_hitbox: Optional[pygame.Rect] = None
        self.attack_has_connected = False

        self.parry_timer = 0.0
        self.parry_cooldown = 0.0
        self.parry_success_flash = 0.0

        self.hit_flash = 0.0

        self.animator = _create_player_animator()
        self.animation_lock = 0.0
        self.pending_feedback: Optional[str] = None
        self.parry_triggered = False
        self.parry_successful = False

    def handle_input(self, keys, dt: float):
        speed = 280
        if self.crouching:
            speed *= 0.6

        self.velocity.x = 0
        if keys[pygame.K_a]:
            self.velocity.x = -speed
            self.facing = -1
        if keys[pygame.K_d]:
            self.velocity.x = speed
            self.facing = 1

        if keys[pygame.K_s] and self.on_ground:
            if not self.crouching:
                self.rect.height = 60
                self.rect.y += 30
            self.crouching = True
        else:
            if self.crouching:
                self.rect.y -= 30
                self.rect.height = 90
            self.crouching = False

        if keys[pygame.K_w] and self.on_ground:
            self.velocity.y = -780
            self.on_ground = False

    def light_attack(self):
        self._trigger_attack(LIGHT_ATTACK)

    def heavy_attack(self):
        self._trigger_attack(HEAVY_ATTACK)

    def _trigger_attack(self, attack: AttackData):
        if self.attack_timer > 0 or self.attack_cooldown > 0:
            return
        if self.stamina < attack.stamina_cost:
            return
        self.stamina -= attack.stamina_cost
        self.attack_timer = attack.duration
        self.attack_cooldown = attack.cooldown
        self.current_attack = attack
        self.attack_hitbox = None
        self.attack_has_connected = False
        self.animation_lock = attack.duration
        if attack is LIGHT_ATTACK:
            self.animator.play("light", force=True)
        else:
            self.animator.play("heavy", force=True)

    def parry(self):
        if self.parry_timer > 0 or self.parry_cooldown > 0:
            return
        if self.stamina < PARRY_COST:
            return
        self.stamina -= PARRY_COST
        self.parry_timer = PARRY_WINDOW
        self.parry_cooldown = PARRY_COOLDOWN
        self.parry_triggered = True
        self.parry_successful = False
        self.animator.play("parry", force=True)
        self.animation_lock = PARRY_WINDOW

    def update(self, dt: float):
        self.velocity.y += GRAVITY * dt

        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.rect.left < 30:
            self.rect.left = 30
        if self.rect.right > WIDTH - 30:
            self.rect.right = WIDTH - 30

        if self.attack_timer > 0 and self.current_attack:
            self.attack_timer = max(0.0, self.attack_timer - dt)
            elapsed = self.current_attack.duration - self.attack_timer
            if self.current_attack.active_start <= elapsed <= self.current_attack.active_end:
                offset = self.current_attack.hitbox_width * self.facing
                self.attack_hitbox = pygame.Rect(
                    self.rect.centerx + offset - self.current_attack.hitbox_width // 2,
                    self.rect.centery - 34,
                    self.current_attack.hitbox_width,
                    68,
                )
            else:
                self.attack_hitbox = None
            if self.attack_timer <= 0:
                self.attack_hitbox = None
                self.current_attack = None
        else:
            self.attack_hitbox = None
            self.current_attack = None

        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        if self.parry_timer > 0:
            self.parry_timer = max(0.0, self.parry_timer - dt)
        if self.parry_cooldown > 0:
            self.parry_cooldown = max(0.0, self.parry_cooldown - dt)
        if self.parry_success_flash > 0:
            self.parry_success_flash = max(0.0, self.parry_success_flash - dt)
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt)

        if self.animation_lock > 0:
            self.animation_lock = max(0.0, self.animation_lock - dt)

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + STAMINA_REGEN * dt)

        if self.parry_timer <= 0 and self.parry_triggered and not self.parry_successful:
            self.pending_feedback = "fail"
            self.parry_triggered = False

        self._update_animation(dt)

    def damage(self, amount: int):
        self.health = max(0, self.health - amount)
        self.hit_flash = 0.25
        self.animator.play("hit", force=True)
        self.animation_lock = 0.2

    def heal_stamina(self, amount: float):
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def register_parry_success(self):
        self.parry_successful = True
        self.parry_triggered = False
        self.pending_feedback = "success"
        self.parry_success_flash = 0.4
        self.animator.play("parry", force=True)
        self.animation_lock = 0.25

    def consume_feedback(self) -> Optional[str]:
        feedback = self.pending_feedback
        self.pending_feedback = None
        return feedback

    def _update_animation(self, dt: float):
        self.animator.set_flip(self.facing == -1)
        if self.animation_lock > 0 and self.animator.current not in {"light", "heavy", "parry", "hit"}:
            # keep forced animation when locked
            pass
        else:
            if self.current_attack is not None:
                if self.current_attack is LIGHT_ATTACK:
                    self.animator.play("light")
                else:
                    self.animator.play("heavy")
            elif self.hit_flash > 0:
                self.animator.play("hit")
            elif self.parry_timer > 0:
                self.animator.play("parry")
            elif not self.on_ground:
                self.animator.play("jump")
            elif self.crouching:
                self.animator.play("crouch")
            elif abs(self.velocity.x) > 10:
                self.animator.play("run")
            else:
                self.animator.play("idle")

        self.animator.update(dt)


class EnemyState(Enum):
    PATROL = auto()
    CHASE = auto()
    WINDUP = auto()
    ATTACK = auto()
    RECOVER = auto()
    STUNNED = auto()


class Enemy:
    def __init__(self, x: float):
        self.rect = pygame.Rect(x, GROUND_Y - 90, 54, 90)
        self.velocity = pygame.Vector2(-120, 0)
        self.max_health = 120
        self.health = self.max_health
        self.facing = -1
        self.patrol_bounds = (WIDTH // 2, WIDTH - 80)

        self.state = EnemyState.PATROL
        self.state_timer = 0.0
        self.attack_rect: Optional[pygame.Rect] = None
        self.hit_flash = 0.0
        self.animator = _create_enemy_animator()
        self.animation_lock = 0.0
        self.animator.play("move")

    def update(self, dt: float, player: Player):
        if self.state == EnemyState.PATROL:
            self._patrol(dt)
            if abs(player.rect.centerx - self.rect.centerx) < 220:
                self._change_state(EnemyState.CHASE, 0)
        elif self.state == EnemyState.CHASE:
            self._chase(dt, player)
        elif self.state == EnemyState.WINDUP:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._change_state(EnemyState.ATTACK, 0.22)
        elif self.state == EnemyState.ATTACK:
            self.state_timer -= dt
            self.attack_rect = pygame.Rect(
                self.rect.centerx + self.facing * 45 - 50,
                self.rect.centery - 35,
                100,
                70,
            )
            if self.state_timer <= 0:
                self.attack_rect = None
                self._change_state(EnemyState.RECOVER, 0.5)
        elif self.state == EnemyState.RECOVER:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._change_state(EnemyState.PATROL, 0)
        elif self.state == EnemyState.STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._change_state(EnemyState.RECOVER, 0.6)

        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt)

        if self.animation_lock > 0:
            self.animation_lock = max(0.0, self.animation_lock - dt)

        self._update_animation(dt)

    def _patrol(self, dt: float):
        self.rect.x += int(self.velocity.x * dt)
        if self.rect.left <= self.patrol_bounds[0]:
            self.rect.left = self.patrol_bounds[0]
            self.velocity.x = abs(self.velocity.x)
            self.facing = 1
        elif self.rect.right >= self.patrol_bounds[1]:
            self.rect.right = self.patrol_bounds[1]
            self.velocity.x = -abs(self.velocity.x)
            self.facing = -1

    def _chase(self, dt: float, player: Player):
        direction = math.copysign(1, player.rect.centerx - self.rect.centerx)
        self.facing = int(direction)
        self.rect.x += int(self.facing * 200 * dt)
        if abs(player.rect.centerx - self.rect.centerx) < 120:
            self._change_state(EnemyState.WINDUP, 0.35)

    def _change_state(self, state: EnemyState, timer: float):
        self.state = state
        self.state_timer = timer
        if state in {EnemyState.WINDUP, EnemyState.ATTACK}:
            self.attack_rect = None
        if state == EnemyState.PATROL:
            self.animator.play("move")
        elif state == EnemyState.CHASE:
            self.animator.play("move")
        elif state == EnemyState.WINDUP:
            self.animator.play("windup", force=True)
            self.animation_lock = timer
        elif state == EnemyState.ATTACK:
            self.animator.play("attack", force=True)
            self.animation_lock = timer
        elif state == EnemyState.RECOVER:
            self.animator.play("idle")
        elif state == EnemyState.STUNNED:
            self.animator.play("stunned", force=True)
            self.animation_lock = timer

    def apply_knockback(self, amount: float, direction: int):
        self.rect.x += int(direction * amount / 2)
        self.rect.x = max(WIDTH // 2, min(self.rect.x, WIDTH - 80))

    def damage(self, amount: int, knockback: float, direction: int):
        self.health = max(0, self.health - amount)
        self.hit_flash = 0.25
        self.apply_knockback(knockback, direction)
        self._change_state(EnemyState.STUNNED, 0.5)
        self.animator.play("hit", force=True)
        self.animation_lock = 0.3

    def parried(self):
        self.attack_rect = None
        self._change_state(EnemyState.STUNNED, 0.75)
        self.hit_flash = 0.3
        self.animator.play("stunned", force=True)
        self.animation_lock = 0.4

    def _update_animation(self, dt: float):
        self.animator.set_flip(self.facing == -1)
        if self.state in {EnemyState.PATROL, EnemyState.CHASE}:
            if self.animation_lock <= 0:
                self.animator.play("move")
        elif self.state == EnemyState.RECOVER and self.animation_lock <= 0:
            self.animator.play("idle")
        self.animator.update(dt)


class CombatGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.player = Player(260)
        self.enemy = Enemy(WIDTH - 220)
        self.mode = GameMode.RUNNING
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.tag_font = pygame.font.Font(None, 26)
        self.big_font = pygame.font.Font(None, 64)
        self.background_gradient, self.background_padding = self._create_gradient()
        self.trail_segments: List[TrailSegment] = []
        self.trail_spawn_timer = 0.0
        self.hit_stop_timer = 0.0
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.shake_offset = pygame.Vector2()
        self.parry_feedback_timer = 0.0
        self.parry_feedback_text = ""
        self.parry_feedback_color = pygame.Color(255, 255, 255)
        self.sounds = self._load_sounds()

    def _create_gradient(self):
        padding = 80
        gradient = pygame.Surface((WIDTH + padding * 2, HEIGHT + padding * 2))
        for y in range(gradient.get_height()):
            t = y / gradient.get_height()
            color = (
                int(25 + 90 * t),
                int(12 + 30 * t),
                int(60 + 140 * (1 - t)),
            )
            pygame.draw.line(gradient, color, (0, y), (gradient.get_width(), y))
        return gradient, padding

    def reset(self):
        self.__init__(self.screen)

    def update(self, dt: float, keys):
        if self.mode != GameMode.RUNNING:
            return
        self.player.handle_input(keys, dt)
        if self.hit_stop_timer > 0:
            self.hit_stop_timer = max(0.0, self.hit_stop_timer - dt)
            effective_dt = 0.0
        else:
            effective_dt = dt

        self.player.update(effective_dt)
        self.enemy.update(effective_dt, self.player)

        if self.trail_spawn_timer > 0:
            self.trail_spawn_timer = max(0.0, self.trail_spawn_timer - dt)
        if self.player.attack_hitbox and self.player.current_attack:
            if self.trail_spawn_timer == 0:
                trail_color = pygame.Color(160, 220, 255)
                if self.player.current_attack is HEAVY_ATTACK:
                    trail_color = pygame.Color(200, 160, 255)
                self._spawn_trail(self.player.attack_hitbox, trail_color)
                self.trail_spawn_timer = 0.05

        self._update_trails(dt)
        self._update_shake(dt)
        self._update_feedback(dt)

        # Player attacks enemy
        if (
            self.player.attack_hitbox
            and self.player.current_attack
            and not self.player.attack_has_connected
            and self.enemy.rect.colliderect(self.player.attack_hitbox)
        ):
            if self.enemy.state != EnemyState.STUNNED:
                self.enemy.damage(
                    self.player.current_attack.damage,
                    self.player.current_attack.knockback,
                    self.player.facing,
                )
            else:
                self.enemy.damage(
                    self.player.current_attack.damage + 6,
                    self.player.current_attack.knockback * 1.2,
                    self.player.facing,
                )
            self.player.attack_has_connected = True
            self._trigger_hit_effects(heavy=self.player.current_attack is HEAVY_ATTACK)
            self._play_sound("hit")

        # Enemy attack vs player
        if self.enemy.attack_rect and self.enemy.state == EnemyState.ATTACK:
            if self.enemy.attack_rect.colliderect(self.player.rect):
                if self.player.parry_timer > 0:
                    self.player.register_parry_success()
                    self.enemy.parried()
                    self.player.heal_stamina(18)
                    self._play_sound("parry")
                else:
                    self.player.damage(18)
                    self.enemy._change_state(EnemyState.RECOVER, 0.8)
                    self._trigger_hit_effects(heavy=False)
                    self._set_feedback("BREAK", pygame.Color(255, 150, 200))
                    self._play_sound("hurt")

        feedback = self.player.consume_feedback()
        if feedback == "success":
            self._set_feedback("PARRY!", pygame.Color(180, 255, 230))
        elif feedback == "fail":
            self._set_feedback("MISS", pygame.Color(255, 190, 130))

        if self.player.health <= 0:
            self.mode = GameMode.DEFEAT
        elif self.enemy.health <= 0:
            self.mode = GameMode.VICTORY

    def draw(self):
        scene = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        offset = (int(self.shake_offset.x), int(self.shake_offset.y))
        bg_position = (offset[0] - self.background_padding, offset[1] - self.background_padding)
        scene.blit(self.background_gradient, bg_position)
        self._draw_arena(scene, offset)
        self._draw_trails(scene, offset)
        self._draw_player(scene, offset)
        self._draw_enemy(scene, offset)
        self.screen.blit(scene, (0, 0))
        self._draw_ui()
        self._draw_feedback()

        if self.mode == GameMode.VICTORY:
            self._draw_banner("VICTORY")
        elif self.mode == GameMode.DEFEAT:
            self._draw_banner("DEFEAT")

    def _draw_arena(self, surface: pygame.Surface, offset):
        ground_rect = pygame.Rect(offset[0], offset[1] + GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
        pygame.draw.rect(surface, (32, 18, 55), ground_rect)
        for x in range(0, WIDTH, 80):
            pygame.draw.polygon(
                surface,
                (70, 45, 95),
                [
                    (x + 20 + offset[0], GROUND_Y + offset[1]),
                    (x + 60 + offset[0], GROUND_Y + offset[1]),
                    (x + 40 + offset[0], GROUND_Y - 30 + offset[1]),
                ],
            )

    def _draw_player(self, surface: pygame.Surface, offset):
        frame = self.player.animator.get_frame()
        pos = (
            self.player.rect.centerx - frame.get_width() // 2 + offset[0],
            self.player.rect.bottom - frame.get_height() + offset[1],
        )
        surface.blit(frame, pos)
        if self.player.parry_success_flash > 0:
            intensity = int(160 * (self.player.parry_success_flash / 0.4))
            overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            overlay.fill((140, 255, 230, intensity))
            surface.blit(overlay, pos, special_flags=pygame.BLEND_RGBA_ADD)
        if self.player.hit_flash > 0:
            intensity = int(150 * (self.player.hit_flash / 0.25))
            overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 80, 80, intensity))
            surface.blit(overlay, pos, special_flags=pygame.BLEND_RGBA_ADD)
        if self.player.attack_hitbox:
            glow = pygame.Surface((self.player.attack_hitbox.width, self.player.attack_hitbox.height), pygame.SRCALPHA)
            glow.fill((120, 200, 255, 70))
            surface.blit(glow, (self.player.attack_hitbox.x + offset[0], self.player.attack_hitbox.y + offset[1]))
        if self.player.parry_timer > 0:
            radius = max(50, 120 * self.player.parry_timer)
            center = (self.player.rect.centerx + offset[0], self.player.rect.centery + offset[1])
            pygame.draw.circle(surface, (140, 220, 255), center, int(radius), 2)
        tag = self.tag_font.render("SOVEREIGN", True, (210, 230, 255))
        surface.blit(tag, (self.player.rect.centerx - tag.get_width() // 2 + offset[0], self.player.rect.top - 32 + offset[1]))

    def _draw_enemy(self, surface: pygame.Surface, offset):
        frame = self.enemy.animator.get_frame()
        pos = (
            self.enemy.rect.centerx - frame.get_width() // 2 + offset[0],
            self.enemy.rect.bottom - frame.get_height() + offset[1],
        )
        surface.blit(frame, pos)
        if self.enemy.hit_flash > 0:
            intensity = int(140 * (self.enemy.hit_flash / 0.3))
            overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 120, 200, intensity))
            surface.blit(overlay, pos, special_flags=pygame.BLEND_RGBA_ADD)
        if self.enemy.attack_rect:
            outline = pygame.Surface((self.enemy.attack_rect.width, self.enemy.attack_rect.height), pygame.SRCALPHA)
            outline.fill((255, 120, 200, 60))
            surface.blit(outline, (self.enemy.attack_rect.x + offset[0], self.enemy.attack_rect.y + offset[1]))
        tag = self.tag_font.render("ECHO SENTINEL", True, (240, 200, 255))
        surface.blit(tag, (self.enemy.rect.centerx - tag.get_width() // 2 + offset[0], self.enemy.rect.top - 32 + offset[1]))

    def _draw_ui(self):
        def draw_bar(x, y, width, height, pct, color_bg, color_fg):
            pygame.draw.rect(self.screen, color_bg, (x, y, width, height))
            pygame.draw.rect(self.screen, color_fg, (x, y, width * pct, height))

        player_pct = self.player.health / self.player.max_health
        player_color = _lerp_color(pygame.Color(40, 220, 160), pygame.Color(255, 60, 90), 1 - player_pct)
        draw_bar(40, 30, 260, 18, player_pct, (60, 40, 70), player_color)
        draw_bar(40, 54, 260, 14, self.player.stamina / self.player.max_stamina, (40, 35, 60), (80, 200, 240))
        self.screen.blit(self.font.render("HEALTH", True, (240, 220, 255)), (40, 10))
        self.screen.blit(self.font.render("STAMINA", True, (220, 220, 255)), (40, 74))

        enemy_pct = self.enemy.health / self.enemy.max_health
        enemy_color = _lerp_color(pygame.Color(190, 120, 255), pygame.Color(255, 70, 150), 1 - enemy_pct)
        draw_bar(WIDTH - 300, 30, 260, 18, enemy_pct, (60, 40, 70), enemy_color)
        self.screen.blit(self.font.render("ENEMY", True, (240, 220, 255)), (WIDTH - 300, 10))

        ability_text = "Abilities locked - progress the myth to awaken powers"
        text = self.font.render(ability_text, True, (200, 200, 220))
        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT - 40))

        controls = "A/D move  W jump  S crouch  1 light  2 heavy  F parry"
        ctrl_text = self.small_font.render(controls, True, (210, 210, 240))
        self.screen.blit(ctrl_text, (WIDTH / 2 - ctrl_text.get_width() / 2, HEIGHT - 70))

    def _draw_trails(self, surface: pygame.Surface, offset):
        for segment in self.trail_segments:
            alpha = int(255 * (segment.life / 0.25))
            if alpha <= 0:
                continue
            trail_surface = pygame.Surface((segment.rect.width, segment.rect.height), pygame.SRCALPHA)
            trail_surface.fill((segment.color.r, segment.color.g, segment.color.b, alpha))
            surface.blit(trail_surface, (segment.rect.x + offset[0], segment.rect.y + offset[1]))

    def _draw_feedback(self):
        if self.parry_feedback_timer <= 0 or not self.parry_feedback_text:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(120 * (self.parry_feedback_timer / 0.6))
        overlay.fill((self.parry_feedback_color.r, self.parry_feedback_color.g, self.parry_feedback_color.b, alpha // 2))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render(self.parry_feedback_text, True, self.parry_feedback_color)
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 140))

    def _draw_banner(self, message: str):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 0, 40, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render(message, True, (255, 255, 255))
        prompt = self.font.render("Press R to reset", True, (230, 230, 255))
        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - 50))
        self.screen.blit(prompt, (WIDTH / 2 - prompt.get_width() / 2, HEIGHT / 2 + 10))

    def _spawn_trail(self, rect: pygame.Rect, color: pygame.Color):
        expanded = rect.inflate(20, 10)
        self.trail_segments.append(TrailSegment(expanded, color, 0.25))

    def _update_trails(self, dt: float):
        alive = []
        for segment in self.trail_segments:
            segment.life -= dt
            if segment.life > 0:
                alive.append(segment)
        self.trail_segments = alive

    def _trigger_hit_effects(self, heavy: bool):
        self.hit_stop_timer = 0.08 if heavy else 0.055
        self.shake_timer = 0.35
        self.shake_magnitude = 10 if heavy else 6

    def _update_shake(self, dt: float):
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
            decay = self.shake_timer / 0.35
            magnitude = self.shake_magnitude * decay
            self.shake_offset.x = random.uniform(-magnitude, magnitude)
            self.shake_offset.y = random.uniform(-magnitude * 0.6, magnitude * 0.6)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0

    def _set_feedback(self, text: str, color: pygame.Color):
        self.parry_feedback_text = text
        self.parry_feedback_color = color
        self.parry_feedback_timer = 0.6

    def _update_feedback(self, dt: float):
        if self.parry_feedback_timer > 0:
            self.parry_feedback_timer = max(0.0, self.parry_feedback_timer - dt)
            if self.parry_feedback_timer == 0:
                self.parry_feedback_text = ""

    def _load_sounds(self):
        sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sounds["hit"] = self._generate_tone(320, 0.12, 0.5)
            sounds["hurt"] = self._generate_tone(140, 0.18, 0.4)
            sounds["parry"] = self._generate_tone(520, 0.1, 0.45)
        except pygame.error:
            # gracefully degrade when audio is unavailable
            return {}
        return sounds

    def _generate_tone(self, frequency: int, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        total_samples = int(sample_rate * duration)
        amplitude = int(32767 * volume)
        buffer = array.array("h")
        for i in range(total_samples):
            sample = int(amplitude * math.sin(2 * math.pi * frequency * (i / sample_rate)))
            buffer.append(sample)
        return pygame.mixer.Sound(buffer=buffer.tobytes(), sample_rate=sample_rate)

    def _play_sound(self, name: str):
        sound = self.sounds.get(name)
        if sound:
            sound.play()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fractal Gods: Sovereign Paradox - Combat Prototype")
    clock = pygame.time.Clock()

    game = CombatGame(screen)

    running = True
    while running:
        dt = clock.tick(60) / 1000
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game.mode == GameMode.RUNNING:
                    if event.key == pygame.K_1:
                        game.player.light_attack()
                    elif event.key == pygame.K_2:
                        game.player.heavy_attack()
                    elif event.key == pygame.K_f:
                        game.player.parry()
                if event.key == pygame.K_r:
                    game.reset()

        game.update(dt, keys)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
