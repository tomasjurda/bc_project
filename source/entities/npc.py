import random

import numpy as np
import pygame

from source.fsm.fsm import FSM
from source.fsm.enemy_states import (
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
    def __init__(
        self, pos, groups, sprite_sheet, collisions, player, brain_type="basic"
    ):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN CREATION
        self.current_collisions = collisions
        self.respawn_pos = pos

        self.hostile = False
        self.player = player
        self.current_target = pygame.Vector2()
        self.path_to_player = []
        self.brain_type = brain_type

        self.brain = DataManager.get_brain(brain_type)

        self.fsm = FSM(self)
        # STATES AND ANIMATIONS
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

        # COOLDOWNS
        self.cooldowns = {"reaction": 0, "stun": 0, "imunity": 0}

        self.hitpoints = self.max_hitpoints = 200
        self.damage = 20
        self.speed = 100

        # AUDIO
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

    def face_player(self):
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

    def get_context_rl(self):
        # 1. Distance
        dist = pygame.Vector2(self.rect.center).distance_to(
            pygame.Vector2(self.player.rect.center)
        )
        normalized_dist = (dist + random.randint(-10, 10)) / 400.0
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

    def get_context(self):
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

    def get_path(self):
        try:
            self.path_to_player = self.g_map.get_path(
                self.rect.center, self.player.rect.center
            )
        except KeyError:
            self.path_to_player = None

    def respawn(self):
        super().respawn()
        self.rect.center = self.respawn_pos
        self.hitbox_rect.center = self.respawn_pos

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()

    def decide_action(self):
        if not self.hostile:
            return SHARED_ACTION_MAP_REVERSED.get("IDLE")

        self.cooldowns["reaction"] = random.triangular(0.3, 0.45, 0.35)
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
            # print(SHARED_ACTION_MAP.get(prediction))
            return prediction
        return SHARED_ACTION_MAP_REVERSED.get("IDLE")

    def draw_ui(self, surface, offset, debug_mode):
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
