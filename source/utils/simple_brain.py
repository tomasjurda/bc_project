from source.core.settings import SHARED_ACTION_MAP_REVERSED


class SimpleBrain:
    def __init__(self):
        pass

    def predict(self, context_data):
        dist = context_data[0]
        npc_stamina = context_data[2]

        if dist > 60:
            return SHARED_ACTION_MAP_REVERSED.get("RUN")

        if npc_stamina >= 0.3:
            return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")

        return SHARED_ACTION_MAP_REVERSED.get("IDLE")
