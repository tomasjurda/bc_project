from i_npc import I_NPC


class HostileNPC(I_NPC):
    def __init__(self, pos, groups, sprite_sheet, collisions, player, brain_type="BASIC"):
        super().__init__(pos, groups, sprite_sheet, collisions, player, brain_type)
        self.hostile = True