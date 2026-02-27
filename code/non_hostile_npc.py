from npc import NPC


class NonHostileNPC(NPC):
    def __init__(
        self,
        pos,
        groups,
        sprite_sheet,
        collisions,
        player,
        npc_data,
        quests,
        brain_type="BASIC",
    ):
        super().__init__(pos, groups, sprite_sheet, collisions, player, brain_type)

        self.quests = quests

        self.hostile = False
        self.affinity = 0

        self.name = npc_data.get("name", "Unknown NPC")
        self.role_description = npc_data.get("role_description", "a generic person.")
        self.greeting_text = npc_data.get("greeting", "Hello.")
        self.quests_data = npc_data.get("quests", {})

        self.chat_history = []

    def update_prompt(self):
        affinity_text = "Neutral."
        if self.affinity < 0:
            affinity_text = (
                "You don't like the player very much. You are distant and cold."
            )
            self.greeting_text = "Ou its you, what do you need?"
        if self.affinity > 2:
            affinity_text = (
                "You like the player. You are very friendly, warm and helpful."
            )
            self.greeting_text = "Hello, friend. What can i do for you?"

        quest_instructions = ""
        for quest_name, quest_states in self.quests_data.items():
            current_state = self.quests.get(quest_name, "not_started")

            if current_state in quest_states:
                quest_instructions += (
                    f"- Quest '{quest_name}': {quest_states[current_state]}\n"
                )

        if not quest_instructions:
            quest_instructions = (
                "- No active quests right now. Just output 'NONE' for the quest update."
            )

        self.prompt_context = f"""
You are {self.name}, {self.role_description} You speak strictly in English.
Your attitude towards the player: {affinity_text}

QUEST INFO:
{quest_instructions}

RULES FOR YOUR RESPONSE:
1. You MUST respond ONLY with a valid JSON object.
2. Do not include any text outside the JSON structure.
3. Keep the "dialogue" value short (1-2 sentences).
4. Use the following JSON schema:
{{
  "dialogue": "Your in-character spoken response goes here.",
  "affinity_change": 0, 
  "quest_update": "NONE"
}}

Note on values:
- "affinity_change": must be an integer. Use +1 (player is nice), -1 (player is rude), or 0 (neutral).
- "quest_update": Use the format "quest_name:state" (e.g., "hammer_quest:accepted") based on QUEST INFO. If none apply, use "NONE".
"""
