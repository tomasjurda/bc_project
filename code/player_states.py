from general_states import *


class Player_Idle(Idle):
    def handle_input(self, player):
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1]:
            player.change_state(player.states["LIGHT_ATTACK"])

        elif mouse[pygame.BUTTON_RIGHT - 1]:
            player.change_state(player.states["HEAVY_ATTACK"])

        elif pressed_keys[pygame.K_r]:
            player.change_state(player.states["BLOCK"])

        elif pressed_keys[pygame.K_SPACE]:
            player.change_state(player.states["DODGE"])

        elif pressed_keys[pygame.K_e]:
            player.interacting = True

        elif keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w]:
            player.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            player.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            if player.direction.length_squared() > 0:
                player.direction.normalize_ip()
                player.update_direction()
                player.change_state(player.states["RUN"])
            else:
                player.change_state(player.states["IDLE"])
            

class Player_Run(Run):
    def handle_input(self, player):
        old_direction_state = player.direction_state
        keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        if mouse[pygame.BUTTON_LEFT - 1]:
            player.change_state(player.states["LIGHT_ATTACK"])

        elif mouse[pygame.BUTTON_RIGHT - 1]:
            player.change_state(player.states["HEAVY_ATTACK"])

        elif pressed_keys[pygame.K_r]:
            player.change_state(player.states["BLOCK"])

        elif pressed_keys[pygame.K_SPACE]:
            player.change_state(player.states["DODGE"])

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
                player.change_state(player.states["IDLE"])
        else:
            player.change_state(player.states["IDLE"])


class Player_Death(State):
    def enter(self, player):
        player.set_animation(speed=5, loop=False)


    def execute(self, player):
        if player.current_animation.finished:
            player.change_state(player.states["IDLE"])
        
    
    def exit(self, player):
        player.is_alive = False
        

class Player_Block(Block):
    def handle_input(self, player):
        old_direction_state = player.direction_state
        keys = pygame.key.get_pressed()
        released_key = pygame.key.get_just_released()

        if released_key[pygame.K_r]:
            player.change_state(player.states["IDLE"])

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


class Player_Stun(Stun):
    def handle_input(self, player):
        pressed_keys = pygame.key.get_just_pressed()
        if pressed_keys[pygame.K_q] and player.stamina >= 4.0:
            player.stamina -= 4.0
            player.cooldowns["stun"] = 0
            player.cooldowns["imunity"] = 0.5
            SoundManager.play_sound(player.sound_effects["break"][0])
            player.change_state(player.states["IDLE"])
            
            
class Player_Heavy_Attack(Heavy_Attack):
    def handle_input(self, player):
        if player.attack_hitbox == None:
            pressed_keys = pygame.key.get_just_pressed()
            if pressed_keys[pygame.K_f]:
                player.change_state(player.states["IDLE"])
                player.stamina += 2.0


class Player_Dialog(State):
    def enter(self, player):
        player.set_animation(speed=8, loop=True) 
