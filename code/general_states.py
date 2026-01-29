from state import State
from settings import *

class Idle(State):
    def enter(self, entity):
        entity.direction = pygame.Vector2()
        entity.set_animation()

class Run(State):
    def enter(self, entity):
        entity.set_animation()
    
    def execute(self, entity):
        entity.move(entity.current_collisions)
    
class Light_Attack(State):
    def enter(self, entity):
        self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 2.0
        entity.cooldowns["attack"] = 0.4
        entity.set_animation(animation_speed = 10)
        entity.attack()


    def execute(self, entity):
        if entity.cooldowns["attack"] <= 0: 
            entity.fsm.change_state(entity.states["idle"])
        

    def exit(self, entity):
        entity.attack_hitbox = None
        entity.set_animation()
        self.attack_end = pygame.time.get_ticks()
        print(self.attack_end - self.attack_start, " ms")


class Heavy_Attack(State):
    def enter(self, entity):
        self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 4.0
        entity.cooldowns["attack"] = 0.4
        entity.set_animation(animation_speed = 10)
        entity.attack()


    def execute(self, entity):
        if entity.cooldowns["attack"] <= 0: 
            entity.fsm.change_state(entity.states["idle"])
        

    def exit(self, entity):
        entity.attack_hitbox = None
        entity.set_animation()
        self.attack_end = pygame.time.get_ticks()
        print(self.attack_end - self.attack_start, " ms")



class Dodge(State):
    def enter(self, entity):
        entity.stamina -= 3.0
        entity.cooldowns["dodge"] = 0.4
        entity.set_animation()


    def execute(self, entity):
        if entity.cooldowns["dodge"] <= 0: 
            entity.fsm.change_state(entity.states["run"])
        elif entity.cooldowns["dodge"] <= 0.2:
            entity.move(entity.current_collisions, 0.5)    
        else:
            entity.move(entity.current_collisions, 3)

class Hurt(State):
    def enter(self, entity):
        entity.cooldowns["stun"] = 0.3
        entity.set_animation()


    def execute(self, entity):
        entity.move(entity.current_collisions)   
        if entity.cooldowns["stun"] <= 0: 
            entity.fsm.change_state(entity.states["idle"])