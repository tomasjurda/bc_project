from settings import *
from FSM import FSM
from i_entity import *
"""
NPCs that are immediatly hostile
"""
class I_Enemy(I_Entity):
    def __init__(self, pos, groups, sprite_sheet, collisions, player):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN CREATION
        self.current_collisions = collisions

        self.player = player
        self.last_player_location = pygame.Vector2()
        self.current_target = pygame.Vector2()
        self.path_to_player = []

        self.fsm = FSM(self)
        self.states = {
            "idle" : Enemy_Idle(),
            "run" : Enemy_Run(),
            "dodge": Dodge(),
            "l_attack": Light_Attack( 2 , 3),
            "h_attack" : Enemy_Heavy_Attack( 3 , 4),
            "hurt" : Hurt(),
            "death" : Enemy_Death(),
            "block" : Enemy_Block()
        }
        
        #CDS + ACTIONS
        self.cooldowns={   # "attack" : 0,
                            #"dodge" : 0,
                            #"respawn": 0,
                            #"stun" : 0,
                            "reaction" : 0 # decision timer
                              }
        
        self.attack_hitbox = None

        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.damage = 20
        self.speed = 100

        
        # AUDIO
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))]
        }

        # ANIMATION
        self.animations = {
            'Enemy_Idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Enemy_Run': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Dodge': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Light_Attack': { 'down' : self.load_frames(6, 5 , False), 'right' :  self.load_frames(7, 5, False), 'left' : self.load_frames(7, 5, True),'up' : self.load_frames(8, 5, False)},
            'Enemy_Heavy_Attack': { 'down' : self.load_frames(13, 6 , False), 'right' :  self.load_frames(14, 6, False), 'left' : self.load_frames(14, 6, True),'up' : self.load_frames(15, 6, False)},
            'Hurt': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Enemy_Death' : { 'down' : self.load_frames(9, 6 , True), 'right' :  self.load_frames(9, 6, False), 'left' : self.load_frames(9, 6, True),'up' : self.load_frames(9, 6, False)},
            'Enemy_Block' : {'down' : self.load_frames(10, 6 , True), 'right' :  self.load_frames(11, 6, False), 'left' : self.load_frames(11, 6, True),'up' : self.load_frames(12, 6, False)}
        }
        self.fsm.change_state(self.states["idle"])

    def get_context(self):
        player = self.player
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
        #print(dist)
        # Zjištění stavu hráče
        player_is_blocking = isinstance(player.fsm.current_state, Player_Block)
        player_is_attacking = isinstance(player.fsm.current_state, (Light_Attack, Heavy_Attack))
        player_stamina_low = player.stamina < 3
        
        # Vlastní stav
        my_stamina_ok = self.stamina > 3
        
        return {
            "dist": dist,
            "p_block": player_is_blocking,
            "p_attack": player_is_attacking,
            "p_low_stamina": player_stamina_low,
            "me_stamina": my_stamina_ok
        }


    def get_path(self):
        self.path_to_player = self.g_map.get_path(self.rect.center , self.last_player_location)
        self.g_map.show_path(self.path_to_player)
        #self.g_map.show_map()
    

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " player_pos: ", (round(self.player.rect.centerx), round(self.player.rect.centery)) ," target: ", self.current_target , " path: ", self.path_to_player)
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " state: ", self.fsm.current_state.__class__.__name__ ," target: ", self.current_target , " path: ", self.path_to_player)
        self.animate()
        

    def decide_action(self):
        self.cooldowns["reaction"] = 0.5
        ctx = self.get_context()
        #print(ctx)
        actions = {} # Akce : Skóre (pravděpodobnost)

        # --- LOGIKA ROZHODOVÁNÍ ---
        
        # 1. Jsem daleko? -> Běžet k hráči
        if ctx["dist"] > 80:
            actions["run"] = 100
            actions["idle"] = 10
        
        # 2. Jsem blízko (v dosahu útoku)?
        elif ctx["dist"] <= 80:
            
            # A) Hráč blokuje? -> HEAVY ATTACK (Guard Break)
            if ctx["p_block"]:
                actions["h_attack"] = 70 if ctx["me_stamina"] else 0
                actions["l_attack"] = 10 # Malá šance, že udělá chybu
                actions["idle"] = 20     # Čekání na chybu hráče
                
            # B) Hráč útočí? -> DODGE nebo BLOCK
            elif ctx["p_attack"]:
                actions["dodge"] = 60 if ctx["me_stamina"] else 0
                actions["block"] = 40
                actions["l_attack"] = 20 # Risk (trade damage)
                
            # C) Hráč nic nedělá (Idle)? -> LIGHT ATTACK (Rychlý poke)
            else:
                actions["l_attack"] = 40
                actions["h_attack"] = 20 # Zkusit ho překvapit
                actions["idle"] = 40
                # Feint logika: Občas zkusit Heavy a zrušit ho
                
        # 3. Mám málo staminy? -> Ustupovat
        if not ctx["me_stamina"]:
            #actions["run_away"] = 50
            actions["block"] = 30 # Želva

        # --- VÝBĚR NEJLEPŠÍ AKCE ---
        # Vybereme akci náhodně, ale s váhou podle skóre
        # (To zajistí, že AI není robotická a občas udělá "chybu" nebo překvapí)
        
        possible_actions = [k for k, v in actions.items() if v > 0]
        weights = [actions[k] for k in possible_actions]
        
        if not possible_actions:
            return "idle"
            
        chosen_action = rand.choices(possible_actions, weights=weights, k=1)[0]
        print(chosen_action)
        return chosen_action    

            

