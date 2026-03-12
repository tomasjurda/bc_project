"""
Module containing the Finite State Machine (FSM) behavior states specific to NPCs and Enemies.
These states hook into the AI decision-making brains (Rule-based, Tree, RL)
instead of listening to keyboard/mouse inputs.
"""

import pygame

from source.core.settings import SHARED_ACTION_MAP
from source.fsm.state import State
from source.fsm.general_states import (
    Idle,
    Run,
    Block,
    Light_Attack,
    Stun,
    Heavy_Attack,
    Dodge,
)


class Enemy_Idle(Idle):
    """
    NPC-specific Idle state. Queries the assigned AI brain for the next action.
    """

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")
            if fin_action in ["RUN", "LIGHT_ATTACK", "HEAVY_ATTACK", "DODGE", "BLOCK"]:
                entity.change_state(entity.states[fin_action])


class Basic_Enemy_Run(Run):
    """
    Simplified run state for basic enemies. They simply run directly
    at the player without utilizing A* pathfinding.
    """

    def enter(self, entity) -> None:
        entity.face_player()
        entity_pos = pygame.Vector2(entity.hitbox_rect.center)
        player_pos = pygame.Vector2(entity.player.hitbox_rect.center)
        dist = entity_pos.distance_to(player_pos)
        if dist < 30:
            entity.direction = entity_pos - player_pos
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
            else:
                entity.direction = pygame.Vector2(-1, 0)
        super().enter(entity)

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")

            if fin_action == "RUN":
                entity.face_player()
                entity_pos = pygame.Vector2(entity.hitbox_rect.center)
                player_pos = pygame.Vector2(entity.player.hitbox_rect.center)
                dist = entity_pos.distance_to(player_pos)
                if dist < 30:
                    entity.direction = entity_pos - player_pos
                    if entity.direction.length_squared() > 0:
                        entity.direction.normalize_ip()
                    else:
                        entity.direction = pygame.Vector2(-1, 0)
                entity.set_animation(loop_start=2, sync_with_current=True)

            elif fin_action in [
                "IDLE",
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
                "DODGE",
                "BLOCK",
            ]:
                entity.change_state(entity.states[fin_action])


class Enemy_Run(Run):
    """
    Advanced run state for smart enemies (Decision Tree / RL).
    Utilizes A* pathfinding nodes to navigate around walls towards the player.
    """

    def enter(self, entity) -> None:
        entity_pos = pygame.Vector2(entity.hitbox_rect.center)
        player_pos = pygame.Vector2(entity.player.hitbox_rect.center)
        dist = entity_pos.distance_to(player_pos)
        if dist < 30:
            entity.direction = entity_pos - player_pos
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
            else:
                entity.direction = pygame.Vector2(-1, 0)
        else:
            entity.get_path()
            if entity.path_to_player:
                entity.current_target = pygame.Vector2(entity.path_to_player.pop(0))
            else:
                entity.change_state(entity.states["IDLE"])
                return
        super().enter(entity)

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")

            if fin_action == "RUN":
                entity_pos = pygame.Vector2(entity.hitbox_rect.center)
                player_pos = pygame.Vector2(entity.player.hitbox_rect.center)
                dist = entity_pos.distance_to(player_pos)
                if dist < 30:
                    entity.direction = entity_pos - player_pos
                    if entity.direction.length_squared() > 0:
                        entity.direction.normalize_ip()
                    else:
                        entity.direction = pygame.Vector2(-1, 0)
                else:
                    entity.get_path()
                    if entity.path_to_player:
                        entity.current_target = pygame.Vector2(
                            entity.path_to_player.pop(0)
                        )
                    else:
                        entity.change_state(entity.states["IDLE"])
                        return
                entity.set_animation(loop_start=2, sync_with_current=True)
            elif fin_action in [
                "IDLE",
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
                "DODGE",
                "BLOCK",
            ]:
                entity.change_state(entity.states[fin_action])

    def execute(self, entity) -> None:
        old_direction_state = entity.direction_state
        entity_pos = pygame.Vector2(entity.rect.center)
        if entity.current_target:
            dist = entity.current_target.distance_to(entity_pos)
            if dist <= 10:
                if entity.path_to_player:
                    entity.current_target = pygame.Vector2(entity.path_to_player.pop(0))
                else:
                    entity.change_state(entity.states["IDLE"])
                    return
            entity.direction = entity.current_target - entity_pos
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
                entity.update_direction()
                if entity.direction_state != old_direction_state:
                    entity.set_animation(loop_start=2, sync_with_current=True)
            else:
                entity.change_state(entity.states["IDLE"])
        else:
            entity.change_state(entity.states["IDLE"])
        super().execute(entity)


class Enemy_Death(State):
    """
    NPC-specific Death state. Disables logic and respawns the enemy for training/testing.
    """

    def enter(self, entity) -> None:
        entity.set_animation(speed=6, loop=False)

    def execute(self, entity) -> None:
        if entity.current_animation.finished:
            entity.change_state(entity.states["IDLE"])

    def exit(self, entity) -> None:
        # entity.kill()
        entity.respawn()


class Enemy_Block(Block):
    """
    NPC-specific block state. Forces the NPC to face the player while blocking.
    """

    def enter(self, entity) -> None:
        entity.face_player()
        super().enter(entity)

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")

            if fin_action == "BLOCK":
                entity.face_player()
                entity.set_animation(loop_start=2, sync_with_current=True)

            elif fin_action in ["IDLE", "RUN", "LIGHT_ATTACK", "HEAVY_ATTACK", "DODGE"]:
                entity.change_state(entity.states[fin_action])


class Enemy_Light_Attack(Light_Attack):
    """
    NPC-specific Light Attack state. Snaps facing direction to the player before swinging.
    """

    def enter(self, entity) -> None:
        entity.face_player()
        super().enter(entity)


class Enemy_Stun(Stun):
    """
    NPC-specific Stun state. Allows smart AI models (like RL) to execute a
    stamina-draining 'Break' action to escape stun locks early.
    """

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")

            if fin_action == "BREAK" and entity.stamina >= 4.0:
                entity.stamina -= 4.0
                entity.cooldowns["stun"] = 0
                entity.cooldowns["imunity"] = 0.5
                entity.sound_effects["break"][0].play()
                entity.change_state(entity.states["IDLE"])


class Enemy_Heavy_Attack(Heavy_Attack):
    """
    NPC-specific Heavy Attack. Allows smart AI models to 'Feint' the attack
    during windup to bait the player into an early parry.
    """

    def enter(self, entity) -> None:
        entity.face_player()
        super().enter(entity)

    def handle_input(self, entity) -> None:
        if entity.cooldowns["reaction"] <= 0 and entity.attack_hitbox is None:
            action = entity.decide_action()
            fin_action = SHARED_ACTION_MAP.get(int(action), "IDLE")

            if fin_action == "FEINT":
                entity.change_state(entity.states["IDLE"])
                entity.stamina += 2.0


class Enemy_Dodge(Dodge):
    """
    NPC-specific Dodge state. Snaps facing direction before rolling.
    """

    def enter(self, entity) -> None:
        entity.face_player()
        super().enter(entity)
