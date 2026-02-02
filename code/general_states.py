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
    def __init__(self, create_hitbox, delete_hitbox):
        self.create_hitbox = create_hitbox
        self.delete_hitbox = delete_hitbox

        
    def enter(self, entity):
        self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 2.0
        entity.set_animation(speed=12 , loop=False)


    def execute(self, entity):
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            entity.attack() # Vytvoří hitbox + zvuk

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None # Deaktivace hitboxu

        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
            self.attack_end = pygame.time.get_ticks()
            print(self.attack_end - self.attack_start, " ms")
        

    def exit(self, entity):
        pass


class Heavy_Attack(State):
    def __init__(self, create_hitbox, delete_hitbox):
        self.create_hitbox = create_hitbox
        self.delete_hitbox = delete_hitbox


    def enter(self, entity):
        self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 4.0
        entity.set_animation(speed=10, loop=False)


    def execute(self, entity):
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            #self.attack_end = pygame.time.get_ticks()
            entity.attack() # Vytvoří hitbox + zvuk

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None # Deaktivace hitboxu

        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
            self.attack_end = pygame.time.get_ticks()
            print(self.attack_end - self.attack_start, " ms")
        

    def exit(self, entity):
        pass


class Dodge(State):
    def enter(self, entity):
        entity.stamina -= 3.0
        entity.set_animation(speed= 20 , loop=False)


    def execute(self, entity):
        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["run"])
        else:
            entity.move(entity.current_collisions, 2.5)


class Hurt(State):
    def enter(self, entity):
        entity.set_animation(speed = 20 , loop=False)


    def execute(self, entity):
        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
        else:
            entity.move(entity.current_collisions)   


class Block(State):
    def enter(self, entity):
        entity.set_animation(speed=6 , loop=True, loop_start=2)
        entity.speed /=  2


    def execute(self, entity):
        entity.move(entity.current_collisions)
        

    def exit(self, entity):
        entity.speed *= 2