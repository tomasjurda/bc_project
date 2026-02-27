from general_states import *

ACTION_MAP = {
    0: "IDLE",
    1: "RUN",
    2: "DODGE",
    3: "BLOCK",
    4: "LIGHT_ATTACK",
    5: "HEAVY_ATTACK",
    6: "FEINT",
    7: "BREAK",
}


class Enemy_Idle(Idle):
    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action in ["RUN", "LIGHT_ATTACK", "HEAVY_ATTACK", "DODGE", "BLOCK"]:
                enemy.change_state(enemy.states[fin_action])


class Basic_Enemy_Run(Run):
    def enter(self, enemy):
        enemy.face_player()
        enemy_pos = pygame.Vector2(enemy.hitbox_rect.center)
        player_pos = pygame.Vector2(enemy.player.hitbox_rect.center)
        dist = enemy_pos.distance_to(player_pos)
        if dist < 30:
            enemy.direction = enemy_pos - player_pos
            if enemy.direction.length_squared() > 0:
                enemy.direction.normalize_ip()
            else:
                enemy.direction = pygame.Vector2(-1, 0)
        super().enter(enemy)

    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action == "RUN":
                enemy.face_player()
                enemy_pos = pygame.Vector2(enemy.hitbox_rect.center)
                player_pos = pygame.Vector2(enemy.player.hitbox_rect.center)
                dist = enemy_pos.distance_to(player_pos)
                if dist < 30:
                    enemy.direction = enemy_pos - player_pos
                    if enemy.direction.length_squared() > 0:
                        enemy.direction.normalize_ip()
                    else:
                        enemy.direction = pygame.Vector2(-1, 0)
                enemy.set_animation(loop_start=2, sync_with_current=True)

            elif fin_action in [
                "IDLE",
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
                "DODGE",
                "BLOCK",
            ]:
                enemy.change_state(enemy.states[fin_action])


class Enemy_Run(Run):
    def enter(self, enemy):
        enemy_pos = pygame.Vector2(enemy.hitbox_rect.center)
        player_pos = pygame.Vector2(enemy.player.hitbox_rect.center)
        dist = enemy_pos.distance_to(player_pos)
        if dist < 30:
            enemy.direction = enemy_pos - player_pos
            if enemy.direction.length_squared() > 0:
                enemy.direction.normalize_ip()
            else:
                enemy.direction = pygame.Vector2(-1, 0)
        else:
            enemy.get_path()
            if enemy.path_to_player:
                enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0))
        super().enter(enemy)

    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action == "RUN":
                enemy_pos = pygame.Vector2(enemy.hitbox_rect.center)
                player_pos = pygame.Vector2(enemy.player.hitbox_rect.center)
                dist = enemy_pos.distance_to(player_pos)
                if dist < 30:
                    enemy.direction = enemy_pos - player_pos
                    if enemy.direction.length_squared() > 0:
                        enemy.direction.normalize_ip()
                    else:
                        enemy.direction = pygame.Vector2(-1, 0)
                else:
                    enemy.get_path()
                    if enemy.path_to_player:
                        enemy.current_target = pygame.Vector2(
                            enemy.path_to_player.pop(0)
                        )
                enemy.set_animation(loop_start=2, sync_with_current=True)
            elif fin_action in [
                "IDLE",
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
                "DODGE",
                "BLOCK",
            ]:
                enemy.change_state(enemy.states[fin_action])

    def execute(self, enemy):
        old_direction_state = enemy.direction_state
        enemy_pos = pygame.Vector2(enemy.rect.center)
        if enemy.current_target:
            dist = enemy.current_target.distance_to(enemy_pos)
            if dist <= 10:
                if enemy.path_to_player:
                    enemy.current_target = pygame.Vector2(enemy.path_to_player.pop(0))
                else:
                    enemy.change_state(enemy.states["IDLE"])
                    return
            enemy.direction = enemy.current_target - enemy_pos
            if enemy.direction.length_squared() > 0:
                enemy.direction.normalize_ip()
                enemy.update_direction()
                if enemy.direction_state != old_direction_state:
                    enemy.set_animation(loop_start=2, sync_with_current=True)
            else:
                enemy.change_state(enemy.states["IDLE"])
        else:
            enemy.change_state(enemy.states["IDLE"])
        super().execute(enemy)


class Enemy_Death(State):
    def enter(self, enemy):
        enemy.set_animation(speed=6, loop=False)

    def execute(self, enemy):
        if enemy.current_animation.finished:
            enemy.change_state(enemy.states["IDLE"])

    def exit(self, enemy):
        # enemy.kill()
        enemy.respawn()


class Enemy_Block(Block):
    def enter(self, enemy):
        enemy.face_player()
        super().enter(enemy)

    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action == "BLOCK":
                enemy.face_player()
                enemy.set_animation(loop_start=2, sync_with_current=True)

            elif fin_action in ["IDLE", "RUN", "LIGHT_ATTACK", "HEAVY_ATTACK", "DODGE"]:
                enemy.change_state(enemy.states[fin_action])


class Enemy_Light_Attack(Light_Attack):
    def enter(self, enemy):
        enemy.face_player()
        super().enter(enemy)


class Enemy_Stun(Stun):
    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action == "BREAK" and enemy.stamina >= 4.0:
                enemy.stamina -= 4.0
                enemy.cooldowns["stun"] = 0
                enemy.cooldowns["imunity"] = 0.5
                SoundManager.play_sound(enemy.sound_effects["break"][0])
                enemy.change_state(enemy.states["IDLE"])


class Enemy_Heavy_Attack(Heavy_Attack):
    def enter(self, enemy):
        enemy.face_player()
        super().enter(enemy)

    def handle_input(self, enemy):
        if enemy.cooldowns["reaction"] <= 0 and enemy.attack_hitbox == None:
            action = enemy.decide_action()
            fin_action = "IDLE"
            if type(action) != str:
                fin_action = ACTION_MAP[int(action)]
            else:
                fin_action = action

            if fin_action == "FEINT":
                enemy.change_state(enemy.states["IDLE"])
                enemy.stamina += 2.0


class Enemy_Dodge(Dodge):
    def enter(self, enemy):
        enemy.face_player()
        super().enter(enemy)
