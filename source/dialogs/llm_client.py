import threading
import ollama


class LLMClient:
    def __init__(self, model_name="llama3.1:8b"):
        self.model_name = model_name
        self.is_generating = False
        self.response_text = None

    def request_response(self, system_prompt, history):
        if self.is_generating:
            return

        self.is_generating = True
        self.response_text = None

        thread = threading.Thread(
            target=self._worker, args=(system_prompt, history), daemon=True
        )
        thread.start()

    def _worker(self, system_prompt, history):
        messages = [{"role": "system", "content": system_prompt}]

        MAX_MESSAGES = 10
        recent_history = history[-MAX_MESSAGES:]

        print(system_prompt)
        for msg in recent_history:
            api_role = "assistant" if msg["role"] == "npc" else "user"
            messages.append(
                {"role": api_role, "content": msg.get("raw_text", msg["text"])}
            )

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format="json",
                options={"temperature": 0.3},
            )
            self.response_text = response["message"]["content"].strip()
            print(self.response_text)
        except (ollama.RequestError, ollama.ResponseError) as e:
            self.response_text = '{{"dialogue": "*Stares at you silently*", "affinity_change": 0, "quest_update": "NONE"}}'
            print(e)
        finally:
            self.is_generating = False
