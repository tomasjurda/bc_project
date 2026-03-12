"""
Module providing shared, generic behavior states that can be inherited
or used by both Players and NPCs within the Finite State Machine (FSM).
"""

import random
import pygame

from source.entities.entity import Entity
from source.fsm.state import State


class Idle(State):
    """
    State representing an entity standing still.
    It clears movement vectors and slowly regenerates stamina.
    """

    def enter(self, entity: Entity) -> None:
        entity.direction = pygame.Vector2()
        entity.set_animation()

    def execute(self, entity: Entity) -> None:
        entity.regen_stamina(coef=4)


class Run(State):
    """
    State representing an entity moving across the map.
    Handles collision sliding and base stamina regeneration.
    """

    def enter(self, entity: Entity) -> None:
        entity.set_animation()

    def execute(self, entity: Entity) -> None:
        entity.regen_stamina()
        entity.move(entity.current_collisions)


class Light_Attack(State):
    """
    State representing a fast, low-damage melee swing.
    Handles precise frame-based hitbox creation and deletion.

    Attributes:
        create_hitbox (int): The animation frame index where the attack becomes lethal.
        delete_hitbox (int): The animation frame index where the attack stops being lethal.
    """

    def __init__(self, create_hitbox: int, delete_hitbox: int) -> None:
        self.create_hitbox = create_hitbox
        self.delete_hitbox = delete_hitbox

    def enter(self, entity: Entity) -> None:
        entity.set_animation(speed=12, loop=False)

    def execute(self, entity: Entity) -> None:
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            entity.create_attack_hitbox()

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None
            if not entity.hit_entities:
                random.choice(entity.sound_effects["miss"]).play()

        if entity.current_animation.finished:
            entity.change_state(entity.states["IDLE"])

    def exit(self, entity: Entity) -> None:
        entity.attack_hitbox = None


class Heavy_Attack(State):
    """
    State representing a slow, high-damage melee swing with a windup.

    Attributes:
        create_hitbox (int): The frame index where the lethal strike begins.
        delete_hitbox (int): The frame index where the strike ends.
    """

    def __init__(self, create_hitbox_index: int, delete_hitbox_index: int) -> None:
        self.create_hitbox = create_hitbox_index
        self.delete_hitbox = delete_hitbox_index

    def enter(self, entity: Entity) -> None:
        entity.set_animation(speed=8, loop=False)

    def execute(self, entity: Entity) -> None:
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            entity.create_attack_hitbox()
            entity.set_animation(speed=12, loop=False, sync_with_current=True)

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None
            if not entity.hit_entities:
                random.choice(entity.sound_effects["miss"]).play()

        if entity.current_animation.finished:
            entity.change_state(entity.states["IDLE"])

    def exit(self, entity: Entity) -> None:
        entity.attack_hitbox = None


class Dodge(State):
    """
    State representing an evasive roll or step.
    Grants temporary invulnerability (i-frames) and burst movement.

    Attributes:
        become_invulnerable (int): Frame index when i-frames begin.
        stop_invulnerable (int): Frame index when i-frames end.
    """

    def __init__(self, become_invulnerable: int, stop_invulnerable: int) -> None:
        self.become_invulnerable = become_invulnerable
        self.stop_invulnerable = stop_invulnerable

    def enter(self, entity: Entity) -> None:
        entity.set_animation(speed=30, loop=False)

    def execute(self, entity: Entity) -> None:
        anim = entity.current_animation
        entity.move(entity.current_collisions, 3)

        if anim.on_frame(self.become_invulnerable):
            entity.is_dodging = True
            entity.sound_effects["dodge"][0].play()

        if anim.on_frame(self.stop_invulnerable):
            entity.is_dodging = False

        if entity.current_animation.finished:
            entity.change_state(entity.states["IDLE"])

    def exit(self, entity: Entity) -> None:
        entity.is_dodging = False


class Stun(State):
    """
    State applied when an entity is hit by an attack.
    Temporarily disables player/AI input and applies physical knockback.
    """

    def enter(self, entity: Entity) -> None:
        entity.set_animation(speed=8, loop=True)

    def execute(self, entity: Entity) -> None:
        entity.regen_stamina()
        if entity.cooldowns["stun"] >= 0.2:
            entity.move(entity.current_collisions, extra=1.5)
        if entity.cooldowns["stun"] <= 0:
            entity.change_state(entity.states["IDLE"])


class Block(State):
    """
    State representing a defensive stance.
    Negates incoming light attack damage. Has a tight parry window at the very beginning.

    Attributes:
        start_blocking (int): Frame index where the block becomes actively defensive.
        stop_blocking (int): Frame index where the block drops.
    """

    def __init__(self, start_blocking: int, stop_blocking: int) -> None:
        self.start_blocking = start_blocking
        self.stop_blocking = stop_blocking

    def enter(self, entity: Entity) -> None:
        entity.set_animation(speed=10, loop=True, loop_start=2)

    def execute(self, entity: Entity) -> None:
        entity.regen_stamina()

        anim = entity.current_animation
        if anim.on_frame(self.start_blocking):
            entity.is_blocking = True
            entity.is_parying = True

        if anim.on_frame(self.start_blocking + 2):
            entity.is_parying = False

        if anim.on_frame(self.stop_blocking):
            entity.is_blocking = False

    def exit(self, entity: Entity) -> None:
        entity.is_blocking = False
        entity.is_parying = False
