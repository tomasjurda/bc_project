from general_states import *
from settings import *
import time as time

class Enemy_Idle(Idle):
    def handle_input(self, enemy):
        #enemy_pos = pygame.Vector2(enemy.rect.center)
        #player_pos = pygame.Vector2(enemy.player.rect.center)
        pressed_keys = pygame.key.get_just_pressed()
        if pressed_keys[pygame.K_b]:
            enemy.fsm.change_state(enemy.states["run"])


class Enemy_Run(Run):
    def handle_input(self, enemy):
        enemy_pos = pygame.Vector2(enemy.rect.center)
        player_pos = pygame.Vector2(enemy.player.rect.center)
        pressed_keys = pygame.key.get_just_pressed()
        if pressed_keys[pygame.K_b]:
            enemy.fsm.change_state(enemy.states["idle"])
            return
        
        if enemy.cooldowns["reaction"] <= 0 and player_pos != enemy.last_player_location:
            enemy.last_player_location = player_pos
            enemy.cooldowns["reaction"] = 0.3
            enemy.get_path()
            if enemy.path_to_player:
                enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
        # If close to current target, move to next point
        if enemy.current_target:
            dist = enemy.current_target.distance_to(enemy_pos)
            if dist <= 10:
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0))
                else:
                    enemy.fsm.change_state(enemy.states["idle"])
                    return
            enemy.direction = enemy.current_target - enemy_pos
            if enemy.direction.length_squared() > 0:
                enemy.direction = enemy.direction.normalize()
            else:
                enemy.direction = pygame.Vector2()
        else:
            enemy.fsm.change_state(enemy.states["idle"])  


class Enemy_Death(State):
    def enter(self, enemy):
        enemy.cooldowns["respawn"] = 1.0
        enemy.set_animation(animation_speed = 5)


    def execute(self, enemy):
        if enemy.cooldowns["respawn"] <= 0:
            enemy.fsm.change_state(enemy.states["idle"])
        
    
    def exit(self, enemy):
        enemy.kill()
        #enemy_respawn()

class Enemy_Block(State):
    pass
        



        