"""
Module handling background communication with local Large Language Models (LLMs) via Ollama.
"""

import threading
import ollama


class LLMClient:
    """
    A client for requesting and receiving dialogue from a local LLM.

    Attributes:
        preferred_model (str): The primary LLM to use (e.g., 'llama3.1:8b').
        fallback_model (str): The backup LLM if the primary fails.
        active_model (str): The model currently being used for generation.
        is_generating (bool): Whether a request is currently being processed.
        response_text (str): The raw JSON string response from the LLM.
        current_session_id (int): Tracker to match threads to current dialogue states.
        response_schema (dict): JSON schema enforcing the LLM's output structure.
    """

    def __init__(self, preferred_model="llama3.1:8b", fallback_model="qwen2.5:3b"):
        """Initializes the LLM Client and determines the active model."""
        self.preferred_model = preferred_model
        self.fallback_model = fallback_model

        self.active_model = preferred_model
        self.is_generating = False
        self.response_text = None

        self.current_session_id = 0

        # Define the strict JSON structure the LLM must follow
        self.response_schema = {
            "type": "object",
            "properties": {
                "thought_process": {
                    "type": "string",
                    "description": "Briefly explain your logic for the dialogue and quest update. E.g., 'The player hasn't paid me yet, so I will ask for money and output NONE.'",
                },
                "dialogue": {
                    "type": "string",
                    "description": "Your spoken response to the player.",
                },
                "affinity_change": {
                    "type": "integer",
                    "enum": [-1, 0, 1],
                    "description": "Change in affinity: -1 (rude), 0 (neutral), or 1 (polite).",
                },
                "quest_update": {
                    "type": "string",
                    "description": "The exact quest state update string, or EXACTLY the word 'NONE'.",
                },
            },
            "required": [
                "thought_process",
                "dialogue",
                "affinity_change",
                "quest_update",
            ],
        }

        # Test which model can be loaded at startup
        threading.Thread(target=self._determine_model, daemon=True).start()

    def _determine_model(self):
        """
        Tests if the preferred model can be loaded into memory.
        Falls back to the smaller model if an exception occurs.
        """
        print(f"Testing {self.preferred_model} for memory limits...")
        try:
            ollama.chat(
                model=self.preferred_model,
                messages=[{"role": "user", "content": "hi"}],
                options={"num_predict": 1},
            )
            self.active_model = self.preferred_model
            print(f"Success! Game will use {self.active_model}.")
        except Exception as e:
            print(f"Failed to load {self.preferred_model}. {e}.")
            print(f"Falling back to {self.fallback_model}...")
            self.active_model = self.fallback_model

    def request_response(self, system_prompt, history):
        """
        Spawns a background worker thread to fetch a response from the LLM.

        Args:
            system_prompt (str): Context and personality instructions for the NPC.
            history (list): A list of recent chat message dictionaries.
        """
        if self.is_generating:
            return

        self.is_generating = True
        self.response_text = None

        self.current_session_id += 1
        session_id = self.current_session_id

        thread = threading.Thread(
            target=self._worker, args=(system_prompt, history, session_id), daemon=True
        )
        thread.start()

    def _worker(self, system_prompt, history, session_id):
        """
        Background worker that makes the Ollama API call.

        Args:
            system_prompt (str): The context instructions for the NPC.
            history (list): A list of recent chat message dictionaries.
            session_id (int): The ID of this generation session.
        """
        messages = [{"role": "system", "content": system_prompt}]

        MAX_MESSAGES = 5
        recent_history = history[-MAX_MESSAGES:]

        for msg in recent_history:
            api_role = "assistant" if msg["role"] == "npc" else "user"
            messages.append(
                {"role": api_role, "content": msg.get("raw_text", msg["text"])}
            )
        try:
            response = ollama.chat(
                model=self.active_model,
                messages=messages,
                format=self.response_schema,
                options={"temperature": 0.4, "top_p": 0.9},
            )
            text = response["message"]["content"].strip()

            if self.current_session_id == session_id:
                self.response_text = text

            print(f"[{self.active_model}] {self.response_text}")
        except (ollama.RequestError, ollama.ResponseError) as e:
            if self.current_session_id == session_id:
                self.response_text = f'{{"thought_process": "Error occurred.", "dialogue": "I cannot speak right now.", "affinity_change": 0, "quest_update": "NONE"}}'
            print(f"Ollama error: {e}")
        finally:
            if self.current_session_id == session_id:
                self.is_generating = False
