"""
Module containing the State Machine class,
responsible for managing and updating an entity's current behavior state.
"""

from source.states.state import State
from source.entities.entity import Entity


class StateMachine:
    """
    A state machine that controls the active state of a game entity.

    Attributes:
        entity (Any): The game entity (Player or NPC) this state machine belongs to.
        current_state (State | None): The currently active behavior state object.
    """

    def __init__(self, entity: Entity) -> None:
        """
        Initializes the StateMachine for a specific entity.

        Args:
            entity (Any): The entity this StateMachine will manage and pass context to.
        """
        self.entity = entity
        self.current_state = None

    def change_state(self, new_state: State) -> None:
        """
        Transitions the entity from the current state to a new state.
        Ensures proper cleanup (exit) of the old state and setup (enter) of the new state.

        Args:
            new_state (State): The newly instantiated state object to transition into.
        """
        if self.current_state:
            self.current_state.exit(self.entity)
        self.current_state = new_state
        self.current_state.enter(self.entity)

    def update(self) -> None:
        """
        Called once per frame by the entity. Processes the active state's
        input checking and continuous logic execution.
        """
        if self.current_state:
            self.current_state.handle_input(self.entity)
            self.current_state.execute(self.entity)
