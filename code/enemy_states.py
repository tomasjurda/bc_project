from general_states import *


class Enemy_Idle(Idle):
    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "RUN":
                enemy.get_path()
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
                enemy.fsm.change_state(enemy.states["run"])
            elif action == "LIGHT_ATTACK" and enemy.stamina >= 2.0:
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "HEAVY_ATTACK" and enemy.stamina >= 4.0:
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "DODGE" and enemy.stamina >= 3.0:
                #print("dodge z idle")
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "BLOCK":
                enemy.fsm.change_state(enemy.states["block"])


class Enemy_Run(Run):
    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "RUN":
                enemy.get_path()
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
            elif action == "LIGHT_ATTACK" and enemy.stamina >= 2.0:
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "HEAVY_ATTACK" and enemy.stamina >= 4.0:
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "DODGE" and enemy.stamina >= 3.0:
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "BLOCK":
                enemy.fsm.change_state(enemy.states["block"])
            elif action == "IDLE":
                enemy.fsm.change_state(enemy.states["idle"])


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
        
        enemy.move(enemy.current_collisions)


class Enemy_Death(State):
    def enter(self, enemy):
        enemy.set_animation(speed = 6, loop = False)


    def execute(self, enemy):
        if enemy.current_animation.finished:
            enemy.fsm.change_state(enemy.states["idle"])
        
    
    def exit(self, enemy):
        #enemy.kill()
        enemy.respawn()


class Enemy_Block(Block):
    def enter(self,enemy):
        enemy.face_player()
        super().enter(enemy)


    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            if action == "RUN":
                enemy.get_path()
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0)) 
                enemy.fsm.change_state(enemy.states["run"])
            elif action == "LIGHT_ATTACK" and enemy.stamina >= 2.0:
                enemy.fsm.change_state(enemy.states["l_attack"])
            elif action == "HEAVY_ATTACK" and enemy.stamina >= 4.0:
                enemy.fsm.change_state(enemy.states["h_attack"])
            elif action == "DODGE" and enemy.stamina >= 3.0:
                enemy.fsm.change_state(enemy.states["dodge"])
            elif action == "IDLE":
                enemy.fsm.change_state(enemy.states["idle"])
            elif action == "BLOCK":
                enemy.face_player()
                enemy.set_animation(loop_start=2, sync_with_current=True)


class Enemy_Light_Attack(Light_Attack):
    def enter(self,enemy):
        enemy.face_player()
        super().enter(enemy)


class Enemy_Heavy_Attack(Heavy_Attack):
    def enter(self,enemy):
        enemy.face_player()
        super().enter(enemy)


    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0 and enemy.attack_hitbox == None:
            action = enemy.decide_action()
            if action == "FEINT":
                enemy.fsm.change_state(enemy.states["idle"])
        