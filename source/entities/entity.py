"""
Module providing the base Entity class, which handles physics, stats,
animations, hitboxes, and state-machine transitions for all living creatures.
"""

from copy import copy
import pygame

from source.utils.grid_map import GridMap
from source.utils.animation import Animation
from source.states.state_machine import StateMachine


class Entity(pygame.sprite.Sprite):
    """
    The base class for all movable characters in the game (Player, NPCs, Enemies).

    Handles foundational mechanics like movement, collision, animation extraction,
    health/stamina management, and combat hitboxes.

    Attributes:
        g_map (GridMap): Shared class-level grid map for pathfinding.
        ysort (bool): Flag indicating this sprite should be depth-sorted.
        dt (float): Delta time for frame-rate independent movement.
        is_blocking (bool): True if currently in a block state.
        is_parying (bool): True if currently in a parry window.
        is_dodging (bool): True if currently invincible during a dodge.
        hitpoints (float): Current health pool.
        stamina (float): Current stamina pool.
        damage (int): Base attack damage.
        state_machine (StateMachine): The state machine instance placeholder.
        direction (pygame.Vector2): Normalized movement vector.
        cooldowns (dict[str, float]): Timers for stun, immunity, etc.
    """

    g_map = GridMap()

    def __init__(
        self,
        pos: tuple[float, float],
        groups: list | tuple,
        sprite_sheet: pygame.Surface,
    ) -> None:
        """
        Initializes the base Entity properties and constructs the core hitboxes.

        Args:
            pos (tuple[float, float]): Initial (x, y) spawn coordinates.
            groups (list | tuple): Pygame sprite groups to attach this entity to.
            sprite_sheet (pygame.Surface): The image grid containing all animations.
        """
        super().__init__(groups)

        self.current_collisions = pygame.sprite.Group()
        self.ysort = True
        self.dt = 0

        # Combat state flags
        self.is_blocking = False
        self.is_parying = False
        self.is_dodging = False

        # Core statistics
        self.hitpoints = self.max_hitpoints = 50
        self.stamina = self.max_stamina = 10.0
        self.damage = 5

        self.hit_entities = []
        self.state_machine = StateMachine(self)

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
        self.states = {}
        self.sound_effects = {}

    def change_state(self, state: dict) -> None:
        """
        Transitions the entity to a new behavior state if stamina allows.

        Args:
            state (dict): A dictionary containing the target 'state' object
                          and its 'stamina_cost'.
        """
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
            self.state_machine.change_state(new_state)

    def load_frames(self, row: int, cols: int, rotate: bool) -> list[pygame.Surface]:
        """
        Extracts a sequence of frames from a specific row in the sprite sheet.

        Args:
            row (int): The row index to extract from.
            cols (int): The number of columns (frames) to extract.
            rotate (bool): If True, horizontally flips the extracted frames.

        Returns:
            list[pygame.Surface]: A list of image surfaces ready for animation.
        """
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

    def respawn(self) -> None:
        """Resets basic health, stamina, and applies temporary respawn immunity."""
        self.hitpoints = self.max_hitpoints
        self.stamina = self.max_stamina
        self.cooldowns["imunity"] = 1.0

    def update_direction(self) -> None:
        """
        Calculates the primary facing direction based on the current movement vector.
        Used to select the correct directional animation frames.
        """
        # Prioritize horizontal facing if moving diagonally
        if abs(self.direction.x) > abs(self.direction.y):
            self.direction_state = "right" if self.direction.x > 0 else "left"
        else:
            self.direction_state = "down" if self.direction.y > 0 else "up"

    def move(self, collision_sprites, extra=1):
        """
        Physically moves the entity using separated X/Y axis steps to allow
        sliding against walls during diagonal movement.

        Args:
            collision_sprites (Iterable): Group of solid environment obstacles.
            extra (float): Speed multiplier modifier (e.g., for dodges).
        """

        self.hitbox_rect.x += self.direction.x * self.speed * self.dt * extra
        self.collision(collision_sprites, "horizontal")

        self.hitbox_rect.y += self.direction.y * self.speed * self.dt * extra
        self.collision(collision_sprites, "vertical")

        # Sync the drawing rect back to the physics hitbox
        self.rect.center = self.hitbox_rect.center

    def collision(self, collision_sprites: pygame.sprite.Group, direction: str) -> None:
        """
        Detects and resolves overlaps with solid map geometry.

        Args:
            collision_sprites (Iterable): Solid obstacles to check against.
            direction (str): Axis being checked ("horizontal" or "vertical").
        """
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

    def draw_ui(
        self, surface: pygame.Surface, offset: pygame.Vector2, debug_mode: bool
    ) -> None:
        """
        Renders floating health bars, stamina bars, and debug visualizations.

        Args:
            surface (pygame.Surface): The main Pygame display surface.
            offset (pygame.Vector2): The current camera scroll offset.
            debug_mode (bool): If True, renders collision hitboxes and state names.
        """
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

    def create_attack_hitbox(self) -> None:
        """
        Spawns an offensive hitbox extending outward in the entity's facing direction.
        Also instantly clears active immunity frames upon launching an attack.
        """
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

    def take_hit(
        self, damage: float, attack_type: int, knockback: pygame.Vector2
    ) -> None:
        """
        Applies incoming damage, forces the entity into a stun/death state,
        and calculates knockback trajectory.

        Args:
            damage (float): Base damage amount.
            attack_type (int): Multiplier type (1=Light, 2=Heavy, 3=Parried Stun).
            knockback (pygame.Vector2): Direction vector pushed away from the attacker.
        """
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

    def set_animation(
        self,
        speed: float = 8.0,
        loop: bool = True,
        loop_start: int = 0,
        sync_with_current: bool = False,
    ) -> None:
        """
        Updates the active animation object to match the current state and direction.

        Args:
            speed (float): Playback frames per second.
            loop (bool): If True, loops continuously.
            loop_start (int): Index to return to on loop restart.
            sync_with_current (bool): If True, tries to maintain the previous animation's
                                      frame index (e.g., smoothly transitioning directions while running).
        """
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

    def animate(self) -> None:
        """
        Advances the animation forward by dt and applies visual effects (like transparency for immunity).
        """
        if self.current_animation:
            self.image = self.current_animation.update(self.dt)
            if self.cooldowns["imunity"] > 0:
                self.image = copy(self.image)
                self.image.set_alpha(128)

    def update_cooldowns(self, dt: float) -> None:
        """Decrements all active time-based trackers."""
        for key, value in self.cooldowns.items():
            if value > 0:
                self.cooldowns[key] = value - dt

    def regen_stamina(self, coef: float = 2.0) -> None:
        """
        Gradually replenishes stamina over time up to the maximum capacity.

        Args:
            coef (float): Base modifier controlling the regeneration speed.
        """
        if self.stamina < 10.0:
            self.stamina += self.dt * coef * 1.5

    def update(self, dt: float) -> None:
        """Placeholder update method designed to be overridden by subclasses."""
