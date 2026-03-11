import json
import pygame

from source.core.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from source.dialogs.llm_client import LLMClient


class DialogUI:
    def __init__(self):
        # UI Layout Settings
        self.height = 250
        self.rect = pygame.Rect(
            10, WINDOW_HEIGHT - self.height - 10, WINDOW_WIDTH - 20, self.height
        )

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)

        # Surface for transparency
        self.surface = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )

        # State
        self.active = False
        self.current_npc = None
        self.player = None
        self.user_input = ""

        self.llm = LLMClient()
        self.provoked_trigger = False
        self.can_type = True

    def start_dialogue(self, player, npc):
        self.active = True
        self.current_npc = npc
        self.player = player
        self.user_input = ""
        self.can_type = True
        self.provoked_trigger = False

        self.current_npc.update_prompt()

        if not self.current_npc.chat_history:
            self.current_npc.chat_history = [
                {
                    "role": "npc",
                    "text": self.current_npc.greeting_text,
                }
            ]

    def close_dialogue(self):
        self.active = False

        self.llm.current_session_id += 1
        self.llm.is_generating = False
        self.llm.response_text = None

        if self.provoked_trigger:
            self.current_npc.hostile = True

        self.current_npc = None
        self.player.change_state(self.player.states["IDLE"])
        self.player = None

    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_dialogue()

            if not self.can_type:
                return

            if event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_RETURN:
                if self.user_input.strip() and not self.llm.is_generating:
                    self.current_npc.chat_history.append(
                        {"role": "user", "text": self.user_input.strip()}
                    )
                    self.llm.request_response(
                        self.current_npc.prompt_context, self.current_npc.chat_history
                    )
                    self.user_input = ""
            else:
                self.user_input += event.unicode

    def update(self):
        if self.llm.response_text:
            try:
                # Očištění případných markdown bloků (např. ```json ... ```)
                clean_json = self.llm.response_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()

                response_data = json.loads(clean_json)
                dialogue = response_data.get("dialogue", "...")
                affinity_change = response_data.get("affinity_change", 0)
                quest_update = response_data.get("quest_update", "NONE")

                self.current_npc.affinity += affinity_change

                if (
                    quest_update != "NONE"
                    and quest_update != ""
                    and ":" in quest_update
                ):
                    q_name, q_state = quest_update.split(":")
                    if q_name != "NONE" and q_state != "NONE":
                        self.current_npc.quests.update_quest(
                            q_name.strip(), q_state.strip()
                        )

                self.current_npc.chat_history.append(
                    {
                        "role": "npc",
                        "text": dialogue,
                        "raw_text": json.dumps(response_data),
                    }
                )

                if self.current_npc.affinity < -2:
                    self.provoked_trigger = True
                    self.can_type = False
                    self.current_npc.chat_history.append(
                        {
                            "role": "system",
                            "text": "The NPC has become hostile! [Press ESC to close]",
                        }
                    )

            except json.JSONDecodeError:
                print("Failed to decode JSON from LLM:", self.llm.response_text)
                self.current_npc.chat_history.append(
                    {
                        "role": "npc",
                        "text": "I... I don't know what to say. (JSON Error)",
                    }
                )

            self.llm.response_text = None

    def wrap_text(self, text, max_width, font):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, display_surface):
        if not self.active or not self.current_npc:
            return

        pygame.draw.rect(
            self.surface, (25, 25, 30, 230), self.surface.get_rect(), border_radius=10
        )
        pygame.draw.rect(
            self.surface,
            (100, 100, 120, 255),
            self.surface.get_rect(),
            width=2,
            border_radius=10,
        )
        display_surface.blit(self.surface, self.rect.topleft)

        chat_width = int(self.rect.width * 0.7)
        info_rect_x = self.rect.x + chat_width

        pygame.draw.line(
            display_surface,
            (100, 100, 120),
            (info_rect_x, self.rect.y + 10),
            (info_rect_x, self.rect.bottom - 10),
            2,
        )

        # LEFT PANEL: CHAT HISTORY & INPUT
        padding = 15
        max_text_width = chat_width - (padding * 2)
        y_offset = self.rect.y + padding
        line_height = self.font.get_linesize()

        # Render the last 3 messages
        for msg in self.current_npc.chat_history[-3:]:
            if msg["role"] == "npc":
                color = (200, 220, 255)  # Light Blue for NPC
                prefix = f"{self.current_npc.name}: "
            elif msg["role"] == "user":
                color = (200, 255, 200)  # Light Green for Player
                prefix = "You: "
            else:
                color = (255, 100, 100)  # Red for System messages
                prefix = "System: "

            full_text = prefix + msg["text"]
            wrapped_lines = self.wrap_text(full_text, max_text_width, self.font)

            for line in wrapped_lines:
                text_surf = self.font.render(line, True, color)
                display_surface.blit(text_surf, (self.rect.x + padding, y_offset))
                y_offset += line_height
            y_offset += 8

        # Render Input Area
        input_y = self.rect.bottom - 40

        pygame.draw.line(
            display_surface,
            (70, 70, 90),
            (self.rect.x + padding, input_y - 5),
            (info_rect_x - padding, input_y - 5),
            1,
        )

        if self.llm.is_generating:
            wait_surf = self.font.render("NPC is thinking...", True, (150, 150, 150))
            display_surface.blit(wait_surf, (self.rect.x + padding, input_y))
        else:
            prefix = "> "
            ellipsis = "..."

            in_surf = self.font.render(prefix + self.user_input, True, (255, 255, 255))

            if in_surf.get_width() > max_text_width:
                available_width = max_text_width - self.font.size(prefix + ellipsis)[0]

                visible_input = ""
                for char in reversed(self.user_input):
                    test_string = char + visible_input
                    if self.font.size(test_string)[0] <= available_width:
                        visible_input = test_string
                    else:
                        break

                final_text = prefix + ellipsis + visible_input
                in_surf = self.font.render(final_text, True, (255, 255, 255))

            display_surface.blit(in_surf, (self.rect.x + padding, input_y))

        # RIGHT PANEL: NPC INFO, QUESTS & MODEL
        info_pad = 15
        info_x = info_rect_x + info_pad
        info_y = self.rect.y + padding

        # NPC Name
        name_surf = self.title_font.render(self.current_npc.name, True, (255, 215, 0))
        display_surface.blit(name_surf, (info_x, info_y))
        info_y += 30

        # Affinity
        aff_color = (200, 200, 200)
        if self.current_npc.affinity > 0:
            aff_color = (100, 255, 100)
        elif self.current_npc.affinity < 0:
            aff_color = (255, 100, 100)

        aff_surf = self.small_font.render(
            f"Affinity: {self.current_npc.affinity}", True, aff_color
        )
        display_surface.blit(aff_surf, (info_x, info_y))
        info_y += 30

        # Active Quests Header
        quest_header = self.font.render("Relevant Quests:", True, (180, 180, 200))
        display_surface.blit(quest_header, (info_x, info_y))
        info_y += 25

        # List Quests and States
        if self.current_npc.quests_data:
            has_quests = False
            for q_name in self.current_npc.quests_data.keys():
                has_quests = True
                q_state = self.current_npc.quests.get_status(q_name)

                # Format: "hammer_quest: accepted"
                q_surf = self.small_font.render(f"- {q_name}:", True, (220, 220, 220))
                display_surface.blit(q_surf, (info_x, info_y))
                info_y += 18

                state_surf = self.small_font.render(
                    f"  [{q_state}]", True, (150, 200, 255)
                )
                display_surface.blit(state_surf, (info_x, info_y))
                info_y += 20

            if not has_quests:
                none_surf = self.small_font.render("None", True, (100, 100, 100))
                display_surface.blit(none_surf, (info_x, info_y))
                info_y += 20
        else:
            none_surf = self.small_font.render("None", True, (100, 100, 100))
            display_surface.blit(none_surf, (info_x, info_y))
            info_y += 20

        # LLM Model display (Bottom Right)
        model_name = getattr(
            self.llm, "active_model", getattr(self.llm, "model_name", "Unknown LLM")
        )
        model_surf = self.small_font.render(
            f"Powered by: {model_name}", True, (100, 100, 100)
        )
        display_surface.blit(model_surf, (info_x, self.rect.bottom - 25))
