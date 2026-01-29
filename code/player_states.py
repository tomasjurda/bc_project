from general_states import *
from settings import *


class Player_Idle(Idle):
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(player.states["l_attack"])
        elif mouse[pygame.BUTTON_RIGHT - 1] and player.stamina >= 4.0:
            player.fsm.change_state(player.states["h_attack"])
            #player.fsm.change_state(player.states["block"])
        elif pressed_keys[pygame.K_e]:
            player.interacting = True
        elif keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w]:
            player.fsm.change_state(player.states["run"])


class Player_Run(Run):
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(player.states["l_attack"])
        elif mouse[pygame.BUTTON_RIGHT - 1] and player.stamina >= 4.0:
            player.fsm.change_state(player.states["h_attack"])
            #player.fsm.change_state(player.states["block"])
        elif pressed_keys[pygame.K_SPACE] and player.stamina >= 3.0:
            player.fsm.change_state(player.states["dodge"])
        elif pressed_keys[pygame.K_e]:
            player.interacting = True
        elif keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]:    
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            player.direction = player.direction.normalize() if player.direction else player.direction
        else:
            player.fsm.change_state(player.states["idle"])


class Player_Death(State):
    def enter(self, player):
        player.cooldowns["respawn"] = 1.0
        player.set_animation(animation_speed = 5)


    def execute(self, player):
        if player.cooldowns["respawn"] <= 0:
            player.fsm.change_state(player.states["idle"])
        
    
    def exit(self, player):
        pass
        #player_respawn()
        

class Player_Block(State):
    def enter(self, player):
        player.set_animation(loop_start = 2, animation_speed = 6)
        player.speed /=  2

    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        released_mouse = pygame.mouse.get_just_released()
        if released_mouse[pygame.BUTTON_RIGHT - 1]:
            player.fsm.change_state(Player_Idle())
        elif keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]:    
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            player.direction = player.direction.normalize() if player.direction else player.direction
        else:
            player.direction = pygame.Vector2()
        

    def execute(self, player):
        player.move(player.current_collisions)
        
    
    def exit(self, player):
        player.speed *= 2

        
