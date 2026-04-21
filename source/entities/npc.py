"""
Module providing the base NPC class, which extends the Entity class.
It adds AI decision-making (Rule-based, Decision Trees, RL), pathfinding,
and context aggregation methods for combat predictions.
"""

import random
import numpy as np
import pygame

from source.states.state_machine import StateMachine
from source.states.enemy_states import (
    Enemy_Idle,
    Enemy_Run,
    Enemy_Block,
    Enemy_Dodge,
    Enemy_Death,
    Enemy_Light_Attack,
    Enemy_Heavy_Attack,
    Enemy_Stun,
)
from source.entities.entity import Entity
from source.utils.sound_manager import SoundManager
from source.utils.data_manager import DataManager
from source.core.settings import (
    SHARED_STATE_MAP,
    SHARED_ACTION_MAP_REVERSED,
)


class NPC(Entity):
    """
    Base class for all Non-Playable Characters (both hostile enemies and friendly townsfolk).

    Integrates with the DataManager to load machine learning models (brains)
    that dictate combat behavior based on the current game state context.

    Attributes:
        current_collisions (pygame.sprite.Group): Group of environment colliders.
        respawn_pos (tuple[float, float]): The original spawn point for resetting.
        hostile (bool): Flag indicating if the NPC should attack the player.
        player (Entity): Reference to the player (or another NPC acting as the target).
        current_target (pygame.Vector2): The immediate coordinate the NPC is walking towards.
        path_to_player (list[tuple]): The A* path nodes currently being followed.
        brain_type (str): Identifier for the AI model used ("basic_offensive", "basic_defensive", "tree", "rl_mlp").
        brain (Any): The loaded AI model instance.
    """

    def __init__(
        self,
        pos: tuple[float, float],
        groups: list | tuple,
        sprite_sheet: pygame.Surface,
        collisions: pygame.sprite.Group,
        player: Entity | None,
        brain_type: str = "basic_offensive",
    ) -> None:
        """
        Initializes the NPC, loads its specified AI brain, and configures its states.

        Args:
            pos (tuple[float, float]): Initial (x, y) spawn coordinates.
            groups (list | tuple): Pygame sprite groups to attach this entity to.
            sprite_sheet (pygame.Surface): The image grid containing animations.
            collisions (pygame.sprite.Group): Environment collision objects.
            player (Entity | None): The primary combat target.
            brain_type (str): The AI model type to load ("basic_offensive", "basic_defensive", "tree", "rl_mlp").
        """
        super().__init__(pos, groups, sprite_sheet)

        # Set during initialization
        self.current_collisions = collisions
        self.respawn_pos = pos

        self.hostile = False
        self.player = player
        self.current_target = pygame.Vector2()
        self.path_to_player = []
        self.brain_type = brain_type

        if brain_type != "rl_training":
            self.brain = DataManager.get_brain(brain_type)

        self.state_machine = StateMachine(self)
        # States and animations
        self.states = {
            "IDLE": {
                "state": Enemy_Idle(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "RUN": {
                "state": Enemy_Run(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "DODGE": {
                "state": Enemy_Dodge(1, 4),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "LIGHT_ATTACK": {
                "state": Enemy_Light_Attack(2, 3),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(6, 5, False),
                    "right": self.load_frames(7, 5, False),
                    "left": self.load_frames(7, 5, True),
                    "up": self.load_frames(8, 5, False),
                },
            },
            "HEAVY_ATTACK": {
                "state": Enemy_Heavy_Attack(3, 4),
                "stamina_cost": 5.0,
                "animation": {
                    "down": self.load_frames(13, 6, False),
                    "right": self.load_frames(14, 6, False),
                    "left": self.load_frames(14, 6, True),
                    "up": self.load_frames(15, 6, False),
                },
            },
            "STUN": {
                "state": Enemy_Stun(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "DEATH": {
                "state": Enemy_Death(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(9, 6, True),
                    "right": self.load_frames(9, 6, False),
                    "left": self.load_frames(9, 6, True),
                    "up": self.load_frames(9, 6, False),
                },
            },
            "BLOCK": {
                "state": Enemy_Block(1, 6),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(10, 6, True),
                    "right": self.load_frames(11, 6, False),
                    "left": self.load_frames(11, 6, True),
                    "up": self.load_frames(12, 6, False),
                },
            },
        }

        # Cooldowns
        self.cooldowns = {"reaction": 0, "stun": 0, "imunity": 0}

        self.hitpoints = self.max_hitpoints = 200
        self.damage = 20
        self.speed = 100

        # Sound effects
        self.sound_effects = {
            "hit": [
                SoundManager.get_sound("sword_hit_1"),
                SoundManager.get_sound("sword_hit_2"),
                SoundManager.get_sound("sword_hit_3"),
            ],
            "miss": [
                SoundManager.get_sound("sword_miss_1"),
                SoundManager.get_sound("sword_miss_2"),
                SoundManager.get_sound("sword_miss_3"),
            ],
            "damage": [
                SoundManager.get_sound("human_damage_1"),
                SoundManager.get_sound("human_damage_2"),
                SoundManager.get_sound("human_damage_3"),
            ],
            "block": [
                SoundManager.get_sound("block_1"),
                SoundManager.get_sound("block_2"),
                SoundManager.get_sound("block_3"),
            ],
            "parry": [
                SoundManager.get_sound("parry"),
                SoundManager.get_sound("parry_1"),
                SoundManager.get_sound("parry_2"),
                SoundManager.get_sound("parry_3"),
            ],
            "dodge": [SoundManager.get_sound("dodge")],
            "break": [SoundManager.get_sound("break")],
        }

        self.change_state(self.states["IDLE"])

    def face_player(self) -> None:
        """
        Calculates the vector pointing towards the player and updates the
        entity's facing direction to visually track them.
        """
        if not self.player:
            return
        vec_to_player = pygame.Vector2(self.player.rect.center) - pygame.Vector2(
            self.rect.center
        )

        if vec_to_player.length_squared() > 0:
            self.direction = vec_to_player.normalize()
            self.update_direction()
        else:
            self.direction = pygame.Vector2()

    def get_context_rl(self) -> list[float]:
        """
        Compiles the normalized combat state into a 1D array specifically
        formatted for the Reinforcement Learning (PPO) Neural Network.

        Returns:
            list[float]: A list of exactly 23 features representing the combat context.
        """
        # 1. Distance
        dist = pygame.Vector2(self.rect.center).distance_to(
            pygame.Vector2(self.player.rect.center)
        )
        normalized_dist = min((dist + random.randint(-10, 10)) / 400.0, 1.0)
        data = [min(max(normalized_dist, 0.0), 1.0)]

        # 2. HP & Stamina
        data.append(self.hitpoints / self.max_hitpoints)
        data.append(self.stamina / self.max_stamina)

        # 3. NPC current action
        idx = SHARED_STATE_MAP.get(self.current_state_name, 0)
        data.extend(np.eye(9)[idx])

        # 4. Player HP & Stamina
        data.append(self.player.hitpoints / self.player.max_hitpoints)
        data.append(self.player.stamina / self.player.max_stamina)

        # 5. Player current action
        idx_p = SHARED_STATE_MAP.get(self.player.current_state_name, 0)
        data.extend(np.eye(9)[idx_p])

        return data

    def get_context(self) -> list[float]:
        """
        Compiles the combat state into a simpler 1D array used by the
        Decision Tree model and the SimpleBrain baseline.

        Returns:
            list[float]: A list of 7 distinct combat variables.
        """
        dist = pygame.Vector2(self.rect.center).distance_to(
            pygame.Vector2(self.player.rect.center)
        )

        return [
            int(dist) + random.randint(-10, 10),
            self.hitpoints / self.max_hitpoints,
            self.stamina / self.max_stamina,
            SHARED_STATE_MAP.get(self.current_state_name, 0),
            self.player.hitpoints / self.player.max_hitpoints,
            self.player.stamina / self.player.max_stamina,
            SHARED_STATE_MAP.get(self.player.current_state_name, 0),
        ]

    def get_path(self) -> None:
        """
        Requests the global GridMap to calculate a smoothed A* path
        from the NPC's current position to the player's position.
        """
        try:
            self.path_to_player = self.g_map.get_path(
                self.rect.center, self.player.rect.center
            )
        except KeyError:
            self.path_to_player = None

    def respawn(self) -> None:
        """Resets stats via the parent Entity class and moves the NPC back to its spawn."""
        super().respawn()
        self.rect.center = self.respawn_pos
        self.hitbox_rect.center = self.respawn_pos

    def update(self, dt: float) -> None:
        """
        Advances the entity logic by one frame.

        Args:
            dt (float): Delta time since last frame.
        """
        self.dt = dt
        self.update_cooldowns(dt)
        self.state_machine.update()
        self.animate()

    def decide_action(self) -> int:
        """
        Queries the assigned AI brain (Simple, Tree, or RL) to determine
        the next tactical combat action.

        Returns:
            int: The integer code representing the chosen action.
        """
        if not self.hostile:
            return SHARED_ACTION_MAP_REVERSED.get("IDLE")

        self.cooldowns["reaction"] = random.triangular(0.2, 0.3, 0.25)
        distance_to_player = pygame.Vector2(self.hitbox_rect.center).distance_to(
            pygame.Vector2(self.player.hitbox_rect.center)
        )

        if self.player.current_state_name != "DEATH" and distance_to_player <= 400:
            if self.brain_type == "rl_mlp":
                ctx = self.get_context_rl()
                prediction = self.brain.predict([ctx])[0][0]
            elif self.brain_type == "tree":
                ctx = self.get_context()
                prediction = self.brain.predict([ctx])[0]
            else:
                # SIMPLE BRAIN
                ctx = self.get_context()
                prediction = self.brain.predict(ctx)

            return prediction
        return SHARED_ACTION_MAP_REVERSED.get("IDLE")

    def draw_ui(
        self, surface: pygame.Surface, offset: pygame.Vector2, debug_mode: bool
    ) -> None:
        """
        Renders standard parent UI elements (healthbars) and adds NPC-specific
        debug visualizations like pathfinding nodes and brain type.

        Args:
            surface (pygame.Surface): The main Pygame display surface.
            offset (pygame.Vector2): Camera scroll offset.
            debug_mode (bool): If True, draws paths and data labels.
        """
        super().draw_ui(surface, offset, debug_mode)
        if debug_mode:
            x = self.rect.x - offset.x
            state_y = self.rect.y - offset.y + self.frame_height
            font = pygame.font.Font(None, 20)

            if self.current_state_name == "RUN":
                if self.path_to_player:
                    for point in self.path_to_player:
                        pygame.draw.rect(
                            surface,
                            "black",
                            (point[0] - offset.x, point[1] - offset.y, 5, 5),
                        )
                if self.current_target:
                    pygame.draw.rect(
                        surface,
                        "black",
                        (
                            self.current_target[0] - offset.x,
                            self.current_target[1] - offset.y,
                            5,
                            5,
                        ),
                    )

            brain_text = font.render(f"{self.brain_type}", True, "white")
            surface.blit(brain_text, (x + 32 - brain_text.width / 2, state_y + 10))

            if not self.hostile:
                aff_text = font.render(f"{self.affinity}", True, "white")
                surface.blit(
                    aff_text,
                    (
                        x + 32 - aff_text.width / 2,
                        state_y + 10 + brain_text.height,
                    ),
                )
