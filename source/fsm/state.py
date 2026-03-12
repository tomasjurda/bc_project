"""
Module defining the base State interface for the Finite State Machine (FSM).
All specific entity behaviors (e.g., Idle, Run, Attack) inherit from this class.
"""

from source.entities.entity import Entity


class State:
    """
    Base class representing a single state within a Finite State Machine.
    Provides structural methods to be overridden by specific behavior subclasses.
    """

    def enter(self, entity: Entity) -> None:
        """
        Called exactly once when the entity transitions into this state.
        Useful for setting up initial animations, sounds, or temporary flags.

        Args:
            entity (Entity): The entity (Player/NPC) executing this state.
        """

    def handle_input(self, entity: Entity) -> None:
        """
        Called every frame to evaluate conditions for transitioning to other states
        (e.g., checking if the player pressed 'Attack' or if an animation finished).

        Args:
            entity (Entity): The entity (Player/NPC) executing this state.
        """

    def execute(self, entity: Entity) -> None:
        """
        Called every frame to perform the state's continuous logic
        (e.g., moving the entity, applying gravity, or draining stamina).

        Args:
            entity (Entity): The entity (Player/NPC) executing this state.
        """

    def exit(self, entity: Entity) -> None:
        """
        Called exactly once when the entity transitions out of this state.
        Useful for cleaning up flags (e.g., deleting attack hitboxes or resetting speeds).

        Args:
            entity (Entity): The entity (Player/NPC) executing this state.
        """
