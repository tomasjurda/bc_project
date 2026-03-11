from copy import copy
import pygame

from source.utils.grid_map import GridMap
from source.utils.animation import Animation


class Entity(pygame.sprite.Sprite):
    g_map = GridMap()

    def __init__(self, pos, groups, sprite_sheet):
        super().__init__(groups)
        self.ysort = True
        self.dt = 0

        self.is_blocking = False
        self.is_parying = False
        self.is_dodging = False

        self.hitpoints = self.max_hitpoints = 50
        self.stamina = self.max_stamina = 10.0
        self.damage = 5

        self.hit_entities = []
        self.fsm = None

        # Basic frame setup and animation
        self.current_state_name = "IDLE"
        self.current_animation = None
        self.frame_width = 64
        self.frame_height = 64
        self.direction_state = "down"

        # Hitbox and sprites
        self.sprite_sheet = sprite_sheet
        self.image = pygame.Surface((self.frame_width, self.frame_height))
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-30, -30)
        self.attack_hitbox = None
        # Movement
        self.direction = pygame.Vector2()
        self.speed = 70
        self.cooldowns = {}

    def change_state(self, state):
        """Changing the state of entity"""
        if self.stamina >= state["stamina_cost"]:
            self.stamina -= state["stamina_cost"]
            new_state = state["state"]
            clean_state_name = (
                new_state.__class__.__name__.replace("Player_", "")
                .replace("Enemy_", "")
                .replace("Basic_", "")
                .upper()
            )
            self.current_state_name = clean_state_name
            self.fsm.change_state(new_state)

    def load_frames(self, row, cols, rotate):
        """Extract frames from a given row in the sprite sheet."""
        frames = []
        for i in range(cols):
            frame = pygame.transform.flip(
                self.sprite_sheet.subsurface(
                    (
                        i * self.frame_width,
                        row * self.frame_height,
                        self.frame_width,
                        self.frame_height,
                    )
                ),
                rotate,
                0,
            )
            frames.append(frame)
        return frames

    def respawn(self):
        """respawn logic"""
        self.hitpoints = self.max_hitpoints
        self.stamina = self.max_stamina
        self.cooldowns["imunity"] = 1.0

    def update_direction(self):
        """Set direction state for animation"""
        if abs(self.direction.x) > abs(self.direction.y):
            self.direction_state = "right" if self.direction.x > 0 else "left"
        else:
            self.direction_state = "down" if self.direction.y > 0 else "up"

    def move(self, collision_sprites, extra=1):
        """method for physically moving the entity with collision detection"""
        self.hitbox_rect.x += self.direction.x * self.speed * self.dt * extra

        self.collision(collision_sprites, "horizontal")
        self.hitbox_rect.y += self.direction.y * self.speed * self.dt * extra

        self.collision(collision_sprites, "vertical")
        self.rect.center = self.hitbox_rect.center

    def collision(self, collision_sprites, direction):
        """method for checking collision for movement"""
        for sprite in collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def draw_ui(self, surface: pygame.Surface, offset, debug_mode):
        """method for basic UI visualisation + debug informations"""
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.hitpoints / self.max_hitpoints
        stamina_ratio = self.stamina / self.max_stamina

        x = self.rect.x - offset.x
        health_y = self.rect.y - offset.y - bar_height * 2
        stamina_y = self.rect.y - offset.y - bar_height

        pygame.draw.rect(surface, "black", (x, health_y, bar_width, bar_height * 2))
        pygame.draw.rect(
            surface, "green", (x, health_y, bar_width * health_ratio, bar_height)
        )
        pygame.draw.rect(
            surface, "yellow", (x, stamina_y, bar_width * stamina_ratio, bar_height)
        )

        if debug_mode:
            state_y = self.rect.y - offset.y + self.frame_height
            font = pygame.font.Font(None, 20)
            state = font.render(f"{self.current_state_name}", True, "white")
            surface.blit(state, (x + 32 - state.width / 2, state_y))

            hitbox_surface = pygame.Surface(
                (self.hitbox_rect.width, self.hitbox_rect.height), pygame.SRCALPHA
            )
            hitbox_col = None
            if self.is_dodging:
                hitbox_col = (0, 0, 0, 128)
            elif self.is_parying:
                hitbox_col = (0, 0, 255, 128)
            elif self.is_blocking:
                hitbox_col = (255, 0, 0, 128)
            else:
                hitbox_col = (0, 255, 0, 128)
            hitbox_surface.fill(hitbox_col)
            surface.blit(
                hitbox_surface,
                (self.hitbox_rect.x - offset.x, self.hitbox_rect.y - offset.y),
            )

    def create_attack_hitbox(self):
        if self.cooldowns["imunity"] > 0:
            self.cooldowns["imunity"] = 0

        self.attack_hitbox = self.hitbox_rect.copy()
        if self.direction_state == "right":
            self.attack_hitbox.midleft = self.hitbox_rect.midright
            self.attack_hitbox.move_ip(-5, 0)

        elif self.direction_state == "left":
            self.attack_hitbox.midright = self.hitbox_rect.midleft
            self.attack_hitbox.move_ip(5, 0)

        elif self.direction_state == "up":
            self.attack_hitbox.midbottom = self.hitbox_rect.midtop
            self.attack_hitbox.move_ip(0, 5)

        else:
            self.attack_hitbox.midtop = self.hitbox_rect.midbottom
            self.attack_hitbox.move_ip(0, -5)

        self.hit_entities = []

    def take_hit(self, damage, attack_type, knockback):
        self.hitpoints -= damage * attack_type

        if self.hitpoints <= 0:
            self.change_state(self.states["DEATH"])
        else:
            self.change_state(self.states["STUN"])
            if attack_type == 3:
                self.cooldowns["stun"] = 1.2
            else:
                self.cooldowns["stun"] = 0.4

            if attack_type == 2:
                self.direction = knockback
            else:
                self.direction = pygame.Vector2()

    def set_animation(self, speed=8, loop=True, loop_start=0, sync_with_current=False):
        frames = self.states[self.current_state_name]["animation"][self.direction_state]

        saved_frame_index = 0
        saved_time = 0

        if sync_with_current and self.current_animation:
            saved_frame_index = self.current_animation.frame_index
            saved_time = self.current_animation.time_accumulator

        self.current_animation = Animation(frames, speed, loop, loop_start)

        if sync_with_current:
            safe_index = saved_frame_index if saved_frame_index < len(frames) else 0
            self.current_animation.frame_index = safe_index
            self.current_animation.time_accumulator = saved_time

        self.image = self.current_animation.frames[
            int(self.current_animation.frame_index)
        ]

    def animate(self):
        if self.current_animation:
            self.image = self.current_animation.update(self.dt)
            if self.cooldowns["imunity"] > 0:
                self.image = copy(self.image)  # self.image.set_alpha(128)
                self.image.set_alpha(128)

    def update_cooldowns(self, dt):
        for key, value in self.cooldowns.items():
            if value > 0:
                self.cooldowns[key] = value - dt

    def regen_stamina(self, coef=2):
        if self.stamina < 10.0:
            self.stamina += self.dt * coef * 1.5

    def update(self, dt):
        pass
