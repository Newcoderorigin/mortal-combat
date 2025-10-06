import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

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


LIGHT_ATTACK = AttackData(
    damage=12,
    stamina_cost=12,
    duration=0.22,
    cooldown=0.35,
    hitbox_width=70,
    knockback=220,
)

HEAVY_ATTACK = AttackData(
    damage=22,
    stamina_cost=22,
    duration=0.36,
    cooldown=0.6,
    hitbox_width=90,
    knockback=320,
)

PARRY_COST = 16
PARRY_WINDOW = 0.25
PARRY_COOLDOWN = 0.6

STAMINA_REGEN = 26  # per second


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

    def parry(self):
        if self.parry_timer > 0 or self.parry_cooldown > 0:
            return
        if self.stamina < PARRY_COST:
            return
        self.stamina -= PARRY_COST
        self.parry_timer = PARRY_WINDOW
        self.parry_cooldown = PARRY_COOLDOWN

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

        if self.attack_timer > 0:
            self.attack_timer -= dt
            offset = self.current_attack.hitbox_width * self.facing
            self.attack_hitbox = pygame.Rect(
                self.rect.centerx + offset - self.current_attack.hitbox_width // 2,
                self.rect.centery - 30,
                self.current_attack.hitbox_width,
                60,
            )
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

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + STAMINA_REGEN * dt)

    def damage(self, amount: int):
        self.health = max(0, self.health - amount)
        self.hit_flash = 0.25

    def heal_stamina(self, amount: float):
        self.stamina = min(self.max_stamina, self.stamina + amount)


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

    def apply_knockback(self, amount: float, direction: int):
        self.rect.x += int(direction * amount / 2)
        self.rect.x = max(WIDTH // 2, min(self.rect.x, WIDTH - 80))

    def damage(self, amount: int, knockback: float, direction: int):
        self.health = max(0, self.health - amount)
        self.hit_flash = 0.25
        self.apply_knockback(knockback, direction)
        self._change_state(EnemyState.STUNNED, 0.5)

    def parried(self):
        self.attack_rect = None
        self._change_state(EnemyState.STUNNED, 0.75)
        self.hit_flash = 0.3


class CombatGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.player = Player(260)
        self.enemy = Enemy(WIDTH - 220)
        self.mode = GameMode.RUNNING
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 64)
        self.background_gradient = self._create_gradient()

    def _create_gradient(self):
        gradient = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (
                int(25 + 90 * t),
                int(12 + 30 * t),
                int(60 + 140 * (1 - t)),
            )
            pygame.draw.line(gradient, color, (0, y), (WIDTH, y))
        return gradient

    def reset(self):
        self.__init__(self.screen)

    def update(self, dt: float, keys):
        if self.mode != GameMode.RUNNING:
            return
        self.player.handle_input(keys, dt)
        self.player.update(dt)
        self.enemy.update(dt, self.player)

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

        # Enemy attack vs player
        if self.enemy.attack_rect and self.enemy.state == EnemyState.ATTACK:
            if self.enemy.attack_rect.colliderect(self.player.rect):
                if self.player.parry_timer > 0:
                    self.player.parry_success_flash = 0.4
                    self.enemy.parried()
                    self.player.heal_stamina(18)
                else:
                    self.player.damage(18)
                    self.enemy._change_state(EnemyState.RECOVER, 0.8)

        if self.player.health <= 0:
            self.mode = GameMode.DEFEAT
        elif self.enemy.health <= 0:
            self.mode = GameMode.VICTORY

    def draw(self):
        self.screen.blit(self.background_gradient, (0, 0))
        self._draw_arena()
        self._draw_player()
        self._draw_enemy()
        self._draw_ui()

        if self.mode == GameMode.VICTORY:
            self._draw_banner("VICTORY")
        elif self.mode == GameMode.DEFEAT:
            self._draw_banner("DEFEAT")

    def _draw_arena(self):
        ground_rect = pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
        pygame.draw.rect(self.screen, (32, 18, 55), ground_rect)
        for x in range(0, WIDTH, 80):
            pygame.draw.polygon(
                self.screen,
                (70, 45, 95),
                [
                    (x + 20, GROUND_Y),
                    (x + 60, GROUND_Y),
                    (x + 40, GROUND_Y - 30),
                ],
            )

    def _draw_player(self):
        color = (180, 210, 255)
        if self.player.hit_flash > 0:
            color = (255, 120, 120)
        elif self.player.parry_success_flash > 0:
            color = (200, 255, 200)
        pygame.draw.rect(self.screen, color, self.player.rect)
        if self.player.attack_hitbox:
            pygame.draw.rect(self.screen, (220, 240, 255), self.player.attack_hitbox, 2)
        if self.player.parry_timer > 0:
            radius = max(50, 120 * self.player.parry_timer)
            center = (self.player.rect.centerx, self.player.rect.centery)
            pygame.draw.circle(self.screen, (120, 200, 255), center, int(radius), 1)

    def _draw_enemy(self):
        color = (230, 180, 255)
        if self.enemy.hit_flash > 0:
            color = (255, 140, 200)
        pygame.draw.rect(self.screen, color, self.enemy.rect)
        if self.enemy.attack_rect:
            pygame.draw.rect(self.screen, (255, 100, 100), self.enemy.attack_rect, 2)

    def _draw_ui(self):
        def draw_bar(x, y, width, height, pct, color_bg, color_fg):
            pygame.draw.rect(self.screen, color_bg, (x, y, width, height))
            pygame.draw.rect(self.screen, color_fg, (x, y, width * pct, height))

        draw_bar(40, 30, 260, 18, self.player.health / self.player.max_health, (60, 40, 70), (180, 60, 120))
        draw_bar(40, 54, 260, 14, self.player.stamina / self.player.max_stamina, (40, 35, 60), (80, 200, 240))
        self.screen.blit(self.font.render("HEALTH", True, (240, 220, 255)), (40, 10))
        self.screen.blit(self.font.render("STAMINA", True, (220, 220, 255)), (40, 74))

        draw_bar(WIDTH - 300, 30, 260, 18, self.enemy.health / self.enemy.max_health, (60, 40, 70), (200, 150, 255))
        self.screen.blit(self.font.render("ENEMY", True, (240, 220, 255)), (WIDTH - 300, 10))

        ability_text = "Abilities locked - progress the myth to awaken powers"
        text = self.font.render(ability_text, True, (200, 200, 220))
        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT - 40))

        controls = "A/D move  W jump  S crouch  1 light  2 heavy  F parry"
        ctrl_text = self.font.render(controls, True, (210, 210, 240))
        self.screen.blit(ctrl_text, (WIDTH / 2 - ctrl_text.get_width() / 2, HEIGHT - 70))

    def _draw_banner(self, message: str):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 0, 40, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render(message, True, (255, 255, 255))
        prompt = self.font.render("Press R to reset", True, (230, 230, 255))
        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - 50))
        self.screen.blit(prompt, (WIDTH / 2 - prompt.get_width() / 2, HEIGHT / 2 + 10))


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
