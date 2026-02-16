from npc import NPC
from settings import *


class RL_Enemy(NPC):
    def __init__(self, pos, groups, sprite_sheet, collisions, player):
        super().__init__(pos, groups, sprite_sheet, collisions, player)

        self.forced_action = 0

        self.current_action = 0
        # Default pro reset
        self.default_pos = pos
        self.hostile = True


    def set_action(self, action_code):
        self.forced_action = action_code


    def decide_action(self):
        if self.cooldowns["reaction"] > 0:
            return self.current_action
        
        new_action = self.forced_action

        if new_action != self.current_action:
            self.current_action = new_action
            self.cooldowns["reaction"] = rand.triangular(0.2, 0.25, 0.22)
            
        return self.current_action