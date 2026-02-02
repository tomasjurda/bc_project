from general_states import *
from settings import *
import time as time

class Enemy_Idle(Idle):
    def handle_input(self, enemy):
        player_pos = pygame.Vector2(enemy.player.rect.center)
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "run":
                enemy.last_player_location = player_pos
                enemy.get_path()
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
                enemy.fsm.change_state(enemy.states["run"])
            elif action == "l_attack":
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "h_attack":
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "dodge":
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "block":
                enemy.fsm.change_state(enemy.states["block"])


class Enemy_Run(Run):
    def handle_input(self, enemy):
        player_pos = pygame.Vector2(enemy.player.rect.center)
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "run":
                enemy.last_player_location = player_pos
                enemy.get_path()
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
            elif action == "l_attack":
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "h_attack":
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "dodge":
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "block":
                enemy.fsm.change_state(enemy.states["block"])


    def execute(self, enemy):
        old_direction_state = enemy.direction_state
        enemy_pos = pygame.Vector2(enemy.rect.center)
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
                enemy.direction.normalize_ip()
                enemy.update_direction()
                if enemy.direction_state != old_direction_state:
                    enemy.set_animation(loop_start=2, sync_with_current=True)
            else:
                enemy.fsm.change_state(enemy.states["idle"])
        else:
            enemy.fsm.change_state(enemy.states["idle"])  
        
        #print(enemy.path_to_player)
        enemy.move(enemy.current_collisions)

class Enemy_Death(State):
    def enter(self, enemy):
        enemy.set_animation(speed = 6, loop = False)


    def execute(self, enemy):
        if enemy.current_animation.finished:
            enemy.fsm.change_state(enemy.states["idle"])
        
    
    def exit(self, enemy):
        enemy.kill()
        #enemy_respawn()


class Enemy_Block(Block):
    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "run":
                enemy.fsm.change_state(enemy.states["run"])
            elif action == "l_attack":
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "h_attack":
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "dodge":
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "block":
                pass


class Enemy_Heavy_Attack(Heavy_Attack):
    def handle_input(self, enemy):
        pass



        