class QuestManager:
    def __init__(self):
        self.quests = {"hammer_quest": "not_started", "city_access": "not_started"}

    def get_status(self, quest_id):
        """Returns the status, or 'unknown' if the quest doesn't exist."""
        return self.quests.get(quest_id, "unknown")

    def update_quest(self, quest_id, new_status):
        """Advances a quest and could potentially trigger UI notifications."""
        if quest_id in self.quests:
            self.quests[quest_id] = new_status
            print(f"Quest Updated: {quest_id} is now '{new_status}'")
