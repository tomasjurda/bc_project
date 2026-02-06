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
        #self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 2.0
        entity.set_animation(speed=12 , loop=False)


    def execute(self, entity):
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            entity.create_attack_hitbox()

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None # Deaktivace hitboxu

        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
            #self.attack_end = pygame.time.get_ticks()
            #print(self.attack_end - self.attack_start, " ms")
        

    def exit(self, entity):
        entity.attack_hitbox = None


class Heavy_Attack(State):
    def __init__(self, create_hitbox_index, delete_hitbox_index):
        self.create_hitbox = create_hitbox_index
        self.delete_hitbox = delete_hitbox_index


    def enter(self, entity):
        #self.attack_start = pygame.time.get_ticks()
        entity.stamina -= 4.0
        entity.set_animation(speed=10, loop=False)


    def execute(self, entity):
        anim = entity.current_animation

        if anim.on_frame(self.create_hitbox):
            #self.attack_end = pygame.time.get_ticks()
            entity.create_attack_hitbox()

        if anim.on_frame(self.delete_hitbox):
            entity.attack_hitbox = None # Deaktivace hitboxu

        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
            #self.attack_end = pygame.time.get_ticks()
            #print(self.attack_end - self.attack_start, " ms")
        

    def exit(self, entity):
        entity.attack_hitbox = None


class Dodge(State):
    def __init__(self, become_invulnerable, stop_invulnerable):
        self.become_invulnerable = become_invulnerable
        self.stop_invulnerable = stop_invulnerable


    def enter(self, entity):
        entity.stamina -= 3.0
        entity.set_animation(speed= 20 , loop=False)


    def execute(self, entity):
        anim = entity.current_animation
        entity.move(entity.current_collisions, 2)

        if anim.on_frame(self.become_invulnerable):
            entity.is_dodging = True

        if anim.on_frame(self.stop_invulnerable):
            entity.is_dodging = False

        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
        

    def exit(self, entity):
        entity.is_dodging = False


class Hurt(State):
    def enter(self, entity):
        entity.set_animation(speed = 20 , loop=False)


    def execute(self, entity):
        entity.move(entity.current_collisions)  
        if entity.current_animation.finished:
            entity.fsm.change_state(entity.states["idle"])
             

class Block(State):
    def __init__(self, start_blocking, stop_blocking):
        self.start_blocking = start_blocking
        self.stop_blocking = stop_blocking


    def enter(self, entity):
        entity.set_animation(speed=8 , loop=True, loop_start=2)
        entity.speed /=  2


    def execute(self, entity):
        anim = entity.current_animation

        if anim.on_frame(self.start_blocking):
            entity.is_blocking = True

        if anim.on_frame(self.stop_blocking):
            entity.is_blocking = False
        

    def exit(self, entity):
        entity.speed *= 2
        entity.is_blocking = False