from settings import *
from i_entity import I_Entity

class Player(I_Entity):
    def __init__(self, pos, groups, collision_sprites, enemy_sprites, interact_sprites ,sprite_sheet):
        super().__init__(pos, groups, collision_sprites)
        self.sprite_sheet = sprite_sheet
        self.max_hitpoints = 100
        self.hitpoints = self.max_hitpoints
        self.damage = 20
        self.enemies = enemy_sprites
        self.interacts = interact_sprites
        self.score = 0
        self.alive = True
        

        # Audio
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))]
        }

        # Animation
        self.animation_speed = 10
        self.animations = {
            'idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'walk': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'dodge': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'attack': { 'down' : self.load_frames(6, 4 , False), 'right' :  self.load_frames(7, 4, False), 'left' : self.load_frames(7, 4, True),'up' : self.load_frames(8, 4, False)},
            'death' : { 'down' : self.load_frames(9, 4 , True), 'right' :  self.load_frames(9, 4, False), 'left' : self.load_frames(9, 4, True),'up' : self.load_frames(9, 4, False)}
                        }
        self.image = self.animations[self.status][self.direction_state][self.frame_index]

        # Movement
        self.speed = 150
        # Attack
        self.attack_cooldown = 500
        self.attack_hitbox = None

        # Dodge
        self.dodging = False
        self.dodge_cooldown = 600
        self.dodge_time = 0


    def take_damage(self, damage, knockback):
        self.hitpoints -= damage
        self.direction = knockback
        play_sound = choice(self.sound_effects['damage'])
        play_sound.set_volume(0.4)
        play_sound.play()
        if self.hitpoints <= 0:
            self.status = 'death'
            self.direction = pygame.Vector2()
            self.frame_index = 0 # Restart animation
            self.animation_speed = 5
        else:
            self.stunned = True
            self.stun_time = pygame.time.get_ticks()
            self.frame_index = 0 # Restart animation
            self.status = 'idle'

    def dodge(self):
        self.dodging = True
        self.dodge_time = pygame.time.get_ticks()
        self.frame_index = 0
        self.status = 'dodge'
        #self.move(10)

    def attack(self):
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.frame_index = 0
        self.status = 'attack'
        self.attack_hitbox = self.hitbox_rect.copy().inflate(-5, -5)
        if self.direction_state == 'right':
            self.attack_hitbox.midleft = self.hitbox_rect.midright
        elif self.direction_state == 'left':
            self.attack_hitbox.midright = self.hitbox_rect.midleft
        elif self.direction_state == 'up':
            self.attack_hitbox.midbottom = self.hitbox_rect.midtop
        else:
            self.attack_hitbox.midtop = self.hitbox_rect.midbottom
        self.attack_colision()

    def attack_colision(self):
        play_sound = choice(self.sound_effects['miss'])
        for enemy in self.enemies:
            if self.attack_hitbox.colliderect(enemy.hitbox_rect):
                enemy.take_damage(self.damage, (pygame.Vector2(enemy.hitbox_rect.center) - pygame.Vector2(self.hitbox_rect.center)).normalize())
                play_sound = choice(self.sound_effects['hit'])
        play_sound.set_volume(0.4)
        play_sound.play()
        
    def heal(self, heal):
        self.hitpoints += heal
        if self.hitpoints > self.max_hitpoints:
            self.hitpoints = self.max_hitpoints

    def respawn(self, pos):
        self.rect.center = pos
        self.hitbox_rect.center = pos
        self.hitpoints = 100
        self.alive = True
        self.direction = pygame.Vector2()
        self.status = 'idle'
        self.direction_state = 'down'
        self.score = 0
        self.attacking = False
        self.animation_speed = 10

    def interact(self):
        for int in self.interacts:
            if self.hitbox_rect.colliderect(int.rect):
                print(int.name)
                return

    def control(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        # Attack
        if mouse[pygame.BUTTON_LEFT - 1] and not self.attacking:
            self.attack()
        elif keys[pygame.K_SPACE] and not self.dodging:
            self.dodge()
        elif keys[pygame.K_e]:
            self.interact()

        # Movement (disabled while attacking)
        if not self.attacking:
            self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            self.direction = self.direction.normalize() if self.direction else self.direction
        else:
            self.direction = pygame.Vector2()
                   
    def animate(self):
        frames = self.animations[self.status][self.direction_state]
        self.time_accumulator += self.dt
        if self.time_accumulator >= 1 / self.animation_speed:
            self.time_accumulator = 0
            self.frame_index += 1

            # Gameover
            if self.status == 'death' and self.frame_index >= len(frames):
                self.alive = False

            # If attack ends, return to idle
            if self.status == 'attack' and self.frame_index >= len(frames):
                #self.attacking = False (attacking for duration of animation)
                self.attack_hitbox =  None
                self.status = 'idle'
                self.frame_index = 0

            self.frame_index %= len(frames)
            self.image = frames[self.frame_index]

    def check_cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.stunned:
            self.move()
            if current_time - self.stun_time >= self.stun_cooldown:
                self.stunned = False
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
        
        if self.dodging:
            if current_time - self.dodge_time <= 200:
                self.move(2)
            if current_time - self.dodge_time >= self.dodge_cooldown:
                self.dodging = False
