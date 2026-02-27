"""Module providing function for working with JSON"""

import json
from settings import *
from llm_client import LLMClient


class DialogUI:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.rect = pygame.Rect(0, WINDOW_HEIGHT - 200, WINDOW_WIDTH, 200)
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.set_alpha(200)
        self.surface.fill((30, 30, 30))

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
                    "raw_text": self.current_npc.greeting_text,
                }
            ]

    def close_dialogue(self):
        self.active = False
        if self.provoked_trigger:
            self.current_npc.hostile = True
        self.current_npc = None
        self.player.change_state(self.player.states["IDLE"])
        self.player = None

    def handle_input(self, event: pygame.event.Event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_dialogue()
            elif event.key == pygame.K_RETURN:
                if self.user_input.strip() and not self.llm.is_generating:
                    self.send_message()
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                if event.unicode.isprintable():
                    self.user_input += event.unicode

    def send_message(self):
        self.current_npc.chat_history.append(
            {"role": "user", "text": self.user_input, "raw_text": self.user_input}
        )
        self.llm.request_response(
            self.current_npc.prompt_context, self.current_npc.chat_history
        )
        self.user_input = ""

    def update(self):
        if self.llm.response_text is not None:
            raw_reply = self.llm.response_text
            self.llm.response_text = None

            try:
                data = json.loads(raw_reply)

                reply_text = data.get("dialogue", "*Stares at you silently*")
                aff_change = data.get("affinity_change", 0)
                quest_data = data.get("quest_update", "NONE")

                # ZPRACOVÁNÍ VZTAHU (Affinity)
                self.current_npc.affinity += int(aff_change)

                # ZPRACOVÁNÍ QUESTŮ (Quests)
                if quest_data != "NONE" and ":" in quest_data:
                    quest_id, new_state = quest_data.split(":")
                    self.current_npc.quests[quest_id.strip()] = new_state.strip()
                    print(f"!!! QUEST UPDATE: {quest_id} -> {new_state} !!!")

            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {raw_reply}")
                reply_text = "*Mutters something incomprehensible...*"
                raw_reply = '{"dialogue": "*Mutters something incomprehensible...*", "affinity_change": 0, "quest_update": "NONE"}'

            # Dočištění textu
            reply_text = reply_text.strip()
            if not reply_text:
                reply_text = "*Stares at you silently*"

            self.current_npc.update_prompt()

            # Kontrola útoku
            if self.current_npc.affinity <= -3:
                self.provoked_trigger = True
                reply_text += " I've had enough of you! Die!"
                self.can_type = False

            self.current_npc.chat_history.append(
                {"role": "npc", "text": reply_text, "raw_text": raw_reply}
            )

    def wrap_text(self, text, max_width):
        lines = []
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = []

            for word in words:
                # Zkusíme přidat slovo k aktuálnímu řádku
                test_line = " ".join(current_line + [word])

                # Změříme, jak široký by řádek byl
                width, _ = self.font.size(test_line)

                if width <= max_width:
                    current_line.append(word)
                else:
                    # Nevejde se, uložíme dosavadní řádek a začneme nový s aktuálním slovem
                    if current_line:  # Jedno slovo delší než celá obrazovka
                        lines.append(" ".join(current_line))
                    current_line = [word]

            # Přidáme poslední řádek
            if current_line:
                lines.append(" ".join(current_line))

        return lines

    def draw(self, display_surface):
        if not self.active:
            return

        display_surface.blit(self.surface, (0, WINDOW_HEIGHT - 200))
        pygame.draw.rect(display_surface, "white", self.rect, 2)

        # Vykreslení historie zpráv se zalamováním
        y_offset = self.rect.y + 10
        padding = 20
        max_text_width = self.rect.width - (padding * 2)
        line_height = self.font.get_linesize()

        for msg in self.current_npc.chat_history[-3:]:
            color = (200, 200, 255) if msg["role"] == "npc" else (200, 255, 200)
            prefix = f"{self.current_npc.name}: " if msg["role"] == "npc" else "You: "
            full_text = prefix + msg["text"]

            wrapped_lines = self.wrap_text(full_text, max_text_width)

            for line in wrapped_lines:
                text_surf = self.font.render(line, True, color)
                display_surface.blit(text_surf, (padding, y_offset))
                y_offset += line_height

            y_offset += 5

        # Input řádek
        input_y = self.rect.bottom - 35
        # Zalamovat můžeme i input
        if self.llm.is_generating:
            wait_surf = self.font.render("NPC is thinking...", True, (150, 150, 150))
            display_surface.blit(wait_surf, (padding, input_y))
        else:
            # Aby hráč viděl konec dlouhého textu, který píše
            visible_input = self.user_input
            in_surf = self.font.render("> " + visible_input, True, "white")

            # Pokud input přesáhne obrazovku, ořízneme ho vizuálně zleva
            if in_surf.get_width() > max_text_width:
                visible_input = "..." + visible_input[-(int(max_text_width // 10)) :]
                in_surf = self.font.render("> " + visible_input, True, "white")

            display_surface.blit(in_surf, (padding, input_y))
