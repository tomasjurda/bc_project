from source.entities.npc import NPC
from source.utils.data_manager import DataManager


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
        self.personal_knowledge = npc_data.get(
            "personal_knowledge", "You only know about your immediate surroundings."
        )
        self.quests_data = npc_data.get("quests", {})

        self.prompt_context = "default"
        self.chat_history = []

    def update_prompt(self):
        affinity_text = "Neutral."
        if self.affinity < 0:
            affinity_text = (
                "You don't like the player very much. You are distant and cold."
            )
        if self.affinity > 2:
            affinity_text = (
                "You like the player. You are very friendly, warm and helpful."
            )

        global_lore = DataManager.get_global_lore()

        quest_instructions = ""
        for quest_name, quest_states in self.quests_data.items():
            current_state = self.quests.get_status(quest_name)

            if current_state in quest_states:
                quest_instructions += (
                    f"- Quest '{quest_name}': {quest_states[current_state]}\n"
                )

        if not quest_instructions:
            quest_instructions = "- No active quests right now. Always output 'NONE' for the quest update."

        self.prompt_context = f"""
You are {self.name}, {self.role_description} You speak strictly in English.
Your attitude towards the player: {affinity_text}

COMMON KNOWLEDGE (Every person in town knows this):
{global_lore}

PERSONAL KNOWLEDGE (Only YOU know this):
{self.personal_knowledge}

QUEST INFO:
{quest_instructions}

RULES FOR YOUR RESPONSE:
1. Fill out "thought_process" FIRST to evaluate what the player actually did versus what they are just talking about.
2. Speak in character. Keep dialogues to 1-2 short sentences.
3. AFFINITY SCORING (DEFAULT TO 0):
   - Give 0 for ALL normal questions, statements, and quest actions (e.g., "I brought the hammer", "Where is the arena?", or "I want to pass" are all 0).
   - ONLY give +1 if the player uses explicit pleasantries (e.g., "Please", "Thank you", "My friend", "Have a great day").
   - ONLY give -1 if the player uses explicit insults, threats, or vulgarity (e.g., "Idiot", "Die", "Give it to me or else").

Note on values:
- "affinity_change": must be EXACTLY -1, 0, or 1 based strictly on Rule 3.
- "quest_update": Output ONLY the exact string specified in QUEST INFO. If the condition for the update is NOT met, output EXACTLY "NONE".

EXAMPLE INTERACTION 1:
Player: "I want to get in, can I bribe you?"
Response: {{"thought_process": "The player is asking to bribe me but hasn't paid. They did not use explicit insults or pleasantries, so affinity is 0.", "dialogue": "Maybe. 10 gold coins might make me look the other way.", "affinity_change": 0, "quest_update": "NONE"}}

EXAMPLE INTERACTION 2:
Player: "I brought your hammer."
Response: {{"thought_process": "The player is turning in a quest. They did not use explicit pleasantries like 'here you go friend', so affinity is 0. I will accept the hammer.", "dialogue": "Finally! Hand it over.", "affinity_change": 0, "quest_update": "hammer_quest:completed"}}
"""

    def take_hit(self, damage, attack_type, knockback):
        if not self.hostile:
            self.hostile = True

        super().take_hit(damage, attack_type, knockback)
