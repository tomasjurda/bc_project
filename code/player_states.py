from state import State
from settings import *


class Player_Idle(State):
    def enter(self, player):
        player.direction = pygame.Vector2()
        player.set_animation()
        #print("entering idle")
    
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        pressed_mouse = pygame.mouse.get_just_pressed()
        if pressed_mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(Player_Attack())
        if pressed_keys[pygame.K_e]:
            player.interacting = True
        elif keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w]:
            player.fsm.change_state(Player_Run())

    def execute(self, player):
        pass

class Player_Run(State):
    def enter(self, player):
        player.set_animation()
        #print("entering walking")
    
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        pressed_mouse = pygame.mouse.get_just_pressed()
        if pressed_mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(Player_Attack())
        elif pressed_keys[pygame.K_SPACE] and player.stamina >= 3.0:
            player.fsm.change_state(Player_Dodge())
        elif pressed_keys[pygame.K_e]:
            player.interacting = True
        elif keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]:    
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            player.direction = player.direction.normalize() if player.direction else player.direction
        else:
            player.fsm.change_state(Player_Idle())

    def execute(self, player):
        player.move(player.current_collisions)


class Player_Attack(State):
    def enter(self, player):
        player.stamina -= 2.0
        player.cooldowns["attack"] = 0.4
        player.set_animation()
        #print("attack")

    def handle_input(self, player):
        pass  # maybe allow left/right control mid-air

    def execute(self, player):
        if player.cooldowns["attack"] <= 0: 
            player.fsm.change_state(Player_Idle())
        else:
            #print(player.cooldowns["attack"] )
            pass
        
    
    def exit(self, player):
        pass
        #print("attack ready")

class Player_Dodge(State):
    def enter(self, player):
        player.stamina -= 3.0
        player.cooldowns["dodge"] = 0.4
        player.set_animation()
        #print("dodge")

    def handle_input(self, player):
        pass  # maybe allow left/right control mid-air

    def execute(self, player):
        if player.cooldowns["dodge"] <= 0: 
            player.fsm.change_state(Player_Run())
        elif player.cooldowns["dodge"] <= 0.2:
            player.move(player.current_collisions, 0.5)    
            pass
        else:
            player.move(player.current_collisions, 3)
        
    
    def exit(self, player):
        pass
        #print("attack ready")



        
