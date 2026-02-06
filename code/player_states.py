from general_states import *


class Player_Idle(Idle):
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(player.states["l_attack"])

        elif mouse[pygame.BUTTON_RIGHT - 1] and player.stamina >= 4.0:
            player.fsm.change_state(player.states["h_attack"])

        elif pressed_keys[pygame.K_r]:
            player.fsm.change_state(player.states["block"])

        elif pressed_keys[pygame.K_SPACE] and player.stamina >= 3.0:
            #print("dodge z idle")
            player.fsm.change_state(player.states["dodge"])

        elif pressed_keys[pygame.K_e]:
            player.interacting = True

        elif keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w]:
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if player.direction.length_squared() > 0:
                player.direction.normalize_ip()
                player.update_direction()
                player.fsm.change_state(player.states["run"])
            else:
                player.fsm.change_state(player.states["idle"])
            

class Player_Run(Run):
    def handle_input(self, player):
        old_direction_state = player.direction_state
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1] and player.stamina >= 2.0:
            player.fsm.change_state(player.states["l_attack"])

        elif mouse[pygame.BUTTON_RIGHT - 1] and player.stamina >= 4.0:
            player.fsm.change_state(player.states["h_attack"])

        elif pressed_keys[pygame.K_r]:
            player.fsm.change_state(player.states["block"])

        elif pressed_keys[pygame.K_SPACE] and player.stamina >= 3.0:
            player.fsm.change_state(player.states["dodge"])

        elif pressed_keys[pygame.K_e]:
            player.interacting = True

        elif keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]:    
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if player.direction.length_squared() > 0:
                player.direction.normalize_ip()
                player.update_direction()
                if player.direction_state != old_direction_state:
                    player.set_animation(loop_start=2, sync_with_current=True)
            else:
                player.fsm.change_state(player.states["idle"])
        else:
            player.fsm.change_state(player.states["idle"])


class Player_Death(State):
    def enter(self, player):
        player.set_animation(speed=5, loop=False)


    def execute(self, player):
        if player.current_animation.finished:
            player.fsm.change_state(player.states["idle"])
        
    
    def exit(self, player):
        player.respawn()
        

class Player_Block(Block):
    def handle_input(self, player):
        old_direction_state = player.direction_state
        keys = pygame.key.get_pressed()
        released_key = pygame.key.get_just_released()

        if released_key[pygame.K_r]:
            player.fsm.change_state(player.states["idle"])

        elif keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_w]:    
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if player.direction.length_squared() > 0:
                player.direction.normalize_ip()
                player.update_direction()
                if player.direction_state != old_direction_state:
                    player.set_animation(loop_start=2, sync_with_current=True)
            else:
                pass
        else:
            player.direction = pygame.Vector2()


class Player_Heavy_Attack(Heavy_Attack):
    def handle_input(self, player):
        if player.attack_hitbox == None:
            pressed_keys = pygame.key.get_just_pressed()
            if pressed_keys[pygame.K_f]:
                player.fsm.change_state(player.states["idle"])

        
