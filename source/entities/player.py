"""
Module defining the Player entity, containing stats, states, and sound effects.
"""

from source.fsm.general_states import Dodge, Light_Attack
from source.fsm.player_states import (
    Player_Idle,
    Player_Run,
    Player_Block,
    Player_Dialog,
    Player_Death,
    Player_Heavy_Attack,
    Player_Stun,
)
from source.fsm.fsm import FSM

from source.entities.entity import Entity
from source.utils.sound_manager import SoundManager


class Player(Entity):
    """
    The main character controlled by the user.

    Inherits from the base Entity class and manages finite state machines,
    combat statistics, animations, and audio effects.

    Attributes:
        current_collisions (pygame.sprite.Group): Group of collidable sprites in the current level.
        respawn_point (dict): Stores the level name and (x, y) position to respawn upon death.
        is_alive (bool): Flag indicating if the player is currently alive.
        interacting (bool): Flag indicating if the player is trying to interact with an object/NPC.
        fsm (FSM): The Finite State Machine controlling player behaviors.
        states (dict): Configuration mapping state names to state objects and animation frames.
        cooldowns (dict): Trackers for time-based cooldowns (e.g., stun, immunity).
        sound_effects (dict): Pre-loaded sound effects mapped to actions.
        ...
    """

    def __init__(self, pos, groups, sprite_sheet):
        """
        Initializes the Player entity at a given position.

        Args:
            pos (tuple | list): Initial (x, y) spawn coordinates.
            groups (list | tuple): Pygame sprite groups to add the player to.
            sprite_sheet (pygame.Surface): The image surface containing animation frames.
        """
        super().__init__(pos, groups, sprite_sheet)

        # This is dynamically updated when switching levels in game.py + current_collisions
        self.respawn_point = {"level": None, "pos": None}

        self.is_alive = True
        self.interacting = False

        # Combat stats
        self.hitpoints = 200
        self.max_hitpoints = 200
        self.damage = 20
        self.speed = 150

        # Initialize the state machine
        self.fsm = FSM(self)

        # States and animations
        # Load_frames parameters are generally: (row_index, frame_count, flip_horizontal)
        self.states = {
            "IDLE": {
                "state": Player_Idle(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "RUN": {
                "state": Player_Run(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "DODGE": {
                "state": Dodge(1, 4),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "LIGHT_ATTACK": {
                "state": Light_Attack(2, 3),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(6, 5, False),
                    "right": self.load_frames(7, 5, False),
                    "left": self.load_frames(7, 5, True),
                    "up": self.load_frames(8, 5, False),
                },
            },
            "HEAVY_ATTACK": {
                "state": Player_Heavy_Attack(3, 4),
                "stamina_cost": 5.0,
                "animation": {
                    "down": self.load_frames(13, 6, False),
                    "right": self.load_frames(14, 6, False),
                    "left": self.load_frames(14, 6, True),
                    "up": self.load_frames(15, 6, False),
                },
            },
            "STUN": {
                "state": Player_Stun(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "DEATH": {
                "state": Player_Death(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(9, 6, True),
                    "right": self.load_frames(9, 6, False),
                    "left": self.load_frames(9, 6, True),
                    "up": self.load_frames(9, 6, False),
                },
            },
            "BLOCK": {
                "state": Player_Block(1, 6),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(10, 6, True),
                    "right": self.load_frames(11, 6, False),
                    "left": self.load_frames(11, 6, True),
                    "up": self.load_frames(12, 6, False),
                },
            },
            "DIALOG": {
                "state": Player_Dialog(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
        }

        # Cooldowns
        self.cooldowns = {"stun": 0, "imunity": 0}

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

        # Initialize the starting state
        self.change_state(self.states["IDLE"])

    def respawn(self):
        """
        Resets the player's stats and triggers the parent Entity respawn logic.
        """
        super().respawn()
        self.is_alive = True

    def update(self, dt):
        """
        Updates the player state, cooldowns, and animations once per frame.

        Args:
            dt (float): Delta time (time elapsed since the last frame).
        """
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()
