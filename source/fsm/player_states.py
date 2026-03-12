"""
Module containing the Finite State Machine (FSM) behavior states specific to the Player.
Handles keyboard/mouse inputs and transitions between combat/movement states.
"""

import pygame

from source.fsm.state import State
from source.fsm.general_states import Idle, Run, Block, Stun, Heavy_Attack


class Player_Idle(Idle):
    """
    Player-specific Idle state. Listens for input to initiate movement or combat.
    """

    def handle_input(self, entity) -> None:
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1]:
            entity.change_state(entity.states["LIGHT_ATTACK"])

        elif mouse[pygame.BUTTON_RIGHT - 1]:
            entity.change_state(entity.states["HEAVY_ATTACK"])

        elif pressed_keys[pygame.K_r]:
            entity.change_state(entity.states["BLOCK"])

        elif pressed_keys[pygame.K_SPACE]:
            entity.change_state(entity.states["DODGE"])

        elif pressed_keys[pygame.K_e]:
            entity.interacting = True

        elif (
            keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w]
        ):
            entity.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            entity.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
                entity.update_direction()
                entity.change_state(entity.states["RUN"])
            else:
                entity.change_state(entity.states["IDLE"])


class Player_Run(Run):
    """
    Player-specific Run state. Allows interrupting movement with attacks/dodges.
    """

    def handle_input(self, entity) -> None:
        old_direction_state = entity.direction_state
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1]:
            entity.change_state(entity.states["LIGHT_ATTACK"])

        elif mouse[pygame.BUTTON_RIGHT - 1]:
            entity.change_state(entity.states["HEAVY_ATTACK"])

        elif pressed_keys[pygame.K_r]:
            entity.change_state(entity.states["BLOCK"])

        elif pressed_keys[pygame.K_SPACE]:
            entity.change_state(entity.states["DODGE"])

        elif pressed_keys[pygame.K_e]:
            entity.interacting = True

        elif (
            keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]
        ):
            entity.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            entity.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
                entity.update_direction()
                if entity.direction_state != old_direction_state:
                    entity.set_animation(loop_start=2, sync_with_current=True)
            else:
                entity.change_state(entity.states["IDLE"])
        else:
            entity.change_state(entity.states["IDLE"])


class Player_Death(State):
    """
    State handling the player's death animation. Disables all input.
    """

    def enter(self, entity) -> None:
        entity.set_animation(speed=5, loop=False)

    def execute(self, entity) -> None:
        if entity.current_animation.finished:
            entity.change_state(entity.states["IDLE"])

    def exit(self, entity) -> None:
        entity.is_alive = False


class Player_Block(Block):
    """
    Player-specific Block state. Allows the player to slowly walk while blocking.
    """

    def handle_input(self, entity) -> None:
        old_direction_state = entity.direction_state
        keys = pygame.key.get_pressed()
        released_key = pygame.key.get_just_released()

        if released_key[pygame.K_r]:
            entity.change_state(entity.states["IDLE"])

        elif (
            keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]
        ):
            entity.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            entity.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if entity.direction.length_squared() > 0:
                entity.direction.normalize_ip()
                entity.update_direction()
                if entity.direction_state != old_direction_state:
                    entity.set_animation(loop_start=2, sync_with_current=True)
            else:
                pass
        else:
            entity.direction = pygame.Vector2()


class Player_Stun(Stun):
    """
    Player-specific Stun state. Allows the player to 'break' out of a stun early
    at the cost of stamina by pressing the Q key.
    """

    def handle_input(self, entity) -> None:
        pressed_keys = pygame.key.get_just_pressed()
        if pressed_keys[pygame.K_q] and entity.stamina >= 4.0:
            entity.stamina -= 4.0
            entity.cooldowns["stun"] = 0
            entity.cooldowns["imunity"] = 0.5
            entity.sound_effects["break"][0].play()
            entity.change_state(entity.states["IDLE"])


class Player_Heavy_Attack(Heavy_Attack):
    """
    Player-specific Heavy Attack. Allows the player to feint (cancel) the attack
    during its windup phase to bait out enemy parries.
    """

    def handle_input(self, entity) -> None:
        if entity.attack_hitbox is None:
            pressed_keys = pygame.key.get_just_pressed()
            if pressed_keys[pygame.K_f]:
                entity.change_state(entity.states["IDLE"])
                entity.stamina += 2.0


class Player_Dialog(State):
    """
    State active while the player is speaking to an NPC.
    Disables all movement and combat inputs until the dialogue UI is closed.
    """

    def enter(self, entity) -> None:
        entity.set_animation(speed=8, loop=True)

    def execute(self, entity) -> None:
        entity.regen_stamina()
