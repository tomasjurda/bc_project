from entity import *


class Player(Entity):
    def __init__(self, pos, groups, sprite_sheet):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN SWITCH_LEVEL
        self.current_collisions = pygame.sprite.Group()
        self.respawn_point = {"level": None, "pos": None}

        self.is_alive = True
        # STATS
        self.hitpoints = self.max_hitpoints = 200
        self.damage = 20
        self.speed = 150

        self.fsm = FSM(self)

        # STATES AND ANIMATIONS
        self.states = {
            "IDLE": {
                "state": Player_Idle(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "RUN": {
                "state": Player_Run(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "DODGE": {
                "state": Dodge(1, 4),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(3, 6, False),
                    "right": self.load_frames(4, 6, False),
                    "left": self.load_frames(4, 6, True),
                    "up": self.load_frames(5, 6, False),
                },
            },
            "LIGHT_ATTACK": {
                "state": Light_Attack(2, 3),
                "stamina_cost": 3.0,
                "animation": {
                    "down": self.load_frames(6, 5, False),
                    "right": self.load_frames(7, 5, False),
                    "left": self.load_frames(7, 5, True),
                    "up": self.load_frames(8, 5, False),
                },
            },
            "HEAVY_ATTACK": {
                "state": Player_Heavy_Attack(3, 4),
                "stamina_cost": 5.0,
                "animation": {
                    "down": self.load_frames(13, 6, False),
                    "right": self.load_frames(14, 6, False),
                    "left": self.load_frames(14, 6, True),
                    "up": self.load_frames(15, 6, False),
                },
            },
            "STUN": {
                "state": Player_Stun(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
            "DEATH": {
                "state": Player_Death(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(9, 6, True),
                    "right": self.load_frames(9, 6, False),
                    "left": self.load_frames(9, 6, True),
                    "up": self.load_frames(9, 6, False),
                },
            },
            "BLOCK": {
                "state": Player_Block(1, 6),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(10, 6, True),
                    "right": self.load_frames(11, 6, False),
                    "left": self.load_frames(11, 6, True),
                    "up": self.load_frames(12, 6, False),
                },
            },
            "DIALOG": {
                "state": Player_Dialog(),
                "stamina_cost": 0.0,
                "animation": {
                    "down": self.load_frames(0, 6, False),
                    "right": self.load_frames(1, 6, False),
                    "left": self.load_frames(1, 6, True),
                    "up": self.load_frames(2, 6, False),
                },
            },
        }

        # COOLDOWNS
        self.cooldowns = {"stun": 0, "imunity": 0}

        self.interacting = False

        # AUDIO
        self.sound_effects = {
            "hit": [
                pygame.mixer.Sound(join("assets", "sword_hit_1.wav")),
                pygame.mixer.Sound(join("assets", "sword_hit_2.wav")),
                pygame.mixer.Sound(join("assets", "sword_hit_3.wav")),
            ],
            "miss": [
                pygame.mixer.Sound(join("assets", "sword_miss_1.wav")),
                pygame.mixer.Sound(join("assets", "sword_miss_2.wav")),
                pygame.mixer.Sound(join("assets", "sword_miss_3.wav")),
            ],
            "damage": [
                pygame.mixer.Sound(join("assets", "human_damage_1.wav")),
                pygame.mixer.Sound(join("assets", "human_damage_2.wav")),
                pygame.mixer.Sound(join("assets", "human_damage_3.wav")),
            ],
            "block": [
                pygame.mixer.Sound(join("assets", "block_1.wav")),
                pygame.mixer.Sound(join("assets", "block_2.wav")),
                pygame.mixer.Sound(join("assets", "block_3.wav")),
            ],
            "parry": [
                pygame.mixer.Sound(join("assets", "parry.wav")),
                pygame.mixer.Sound(join("assets", "parry_1.wav")),
                pygame.mixer.Sound(join("assets", "parry_2.wav")),
                pygame.mixer.Sound(join("assets", "parry_3.wav")),
            ],
            "dodge": [pygame.mixer.Sound(join("assets", "dodge.wav"))],
            "break": [pygame.mixer.Sound(join("assets", "break.wav"))],
        }

        self.change_state(self.states["IDLE"])

    def respawn(self):
        super().respawn()
        self.is_alive = True

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()
