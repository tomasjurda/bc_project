"""
Module containing the QuestManager, which tracks global progress,
event flags, and story progression.
"""


class QuestManager:
    """
    Manages global story state and tracks the progression of active quests.
    Used dynamically by LLM-driven NPCs to understand player progress.

    Attributes:
        quests (dict[str, str]): Dictionary mapping quest IDs to their current status.
    """

    _quests = {"hammer_quest": "not_started", "city_access": "not_started"}

    @classmethod
    def get_status(cls, quest_id: str) -> str:
        """
        Returns the current status of a given quest.

        Args:
            quest_id (str): The unique identifier key of the quest.

        Returns:
            str: The quest's current status string, or 'unknown' if the quest doesn't exist.
        """
        return cls._quests.get(quest_id, "unknown")

    @classmethod
    def update_quest(cls, quest_id: str, new_status: str) -> None:
        """
        Advances or changes the status of a specific quest.

        Args:
            quest_id (str): The unique identifier key of the quest to modify.
            new_status (str): The updated status string for the quest.
        """
        if quest_id in cls._quests:
            cls._quests[quest_id] = new_status
            print(f"Quest Updated: {quest_id} is now '{new_status}'")
