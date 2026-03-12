"""
Module defining the NonHostileNPC class. This entity handles dynamic,
LLM-driven conversations, quest tracking, and affinity systems.
"""

import pygame

from source.entities.player import Player
from source.entities.npc import NPC

from source.utils.data_manager import DataManager
from source.utils.quest_manager import QuestManager


class NonHostileNPC(NPC):
    """
    A subclass of NPC representing a neutral or friendly character.
    These NPCs can be spoken to via the DialogUI, update quest states,
    and maintain an affinity score based on how the player treats them.

    Attributes:
        quests (QuestManager): Reference to the global QuestManager.
        affinity (int): Numerical representation of how much the NPC likes the player.
        name (str): The NPC's display name.
        role_description (str): Background information injected into the LLM prompt.
        greeting_text (str): The very first message the NPC says when spoken to.
        personal_knowledge (str): Secret or specific lore known only to this NPC.
        quests_data (dict): Dictionary defining quests this NPC interacts with.
        prompt_context (str): The compiled system prompt fed to the LLM.
        chat_history (list[dict]): Running log of the conversation.
    """

    def __init__(
        self,
        pos: tuple[float, float],
        groups: list | tuple,
        sprite_sheet: pygame.Surface,
        collisions: pygame.sprite.Group,
        player: Player,
        npc_data: dict,
        quests: QuestManager,
        brain_type: str = "BASIC",
    ) -> None:
        """
        Initializes the friendly NPC with its dialogue configuration and personality.

        Args:
            pos (tuple[float, float]): Initial (x, y) spawn coordinates.
            groups (list | tuple): Pygame sprite groups to attach this entity to.
            sprite_sheet (pygame.Surface): The image grid containing animations.
            collisions (pygame.sprite.Group): Environment collision objects.
            player (Player): Reference to the player entity.
            npc_data (dict): Dictionary containing name, lore, and quest rules from JSON.
            quests (QuestManager): Reference to the global QuestManager.
            brain_type (str): The AI combat model to use if the NPC becomes hostile.
        """
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

    def update_prompt(self) -> None:
        """
        Dynamically constructs the system prompt instructing the local LLM.
        It pulls current affinity, global lore, and the specific status of active quests
        so the NPC acts appropriately to the exact current game state.
        """
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

    def take_hit(
        self, damage: float, attack_type: int, knockback: pygame.Vector2
    ) -> None:
        """
        Overrides the standard Entity damage handler.
        If the player attacks this friendly NPC, they immediately become hostile
        and will start fighting back using their assigned AI brain.

        Args:
            damage (float): The amount of damage dealt.
            attack_type (int): The type multiplier of the attack (light, heavy, parry).
            knockback (pygame.Vector2): The directional vector to push the NPC.
        """
        if not self.hostile:
            self.hostile = True

        super().take_hit(damage, attack_type, knockback)
