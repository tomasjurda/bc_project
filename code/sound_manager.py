from settings import *

class SoundManager():
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.last_played_time = 0
        self.volume = 0.4

    def play_sound(self, sound : pygame.mixer.Sound):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_played_time < 100:
            return
        sound.set_volume(self.volume)
        sound.play()
        self.last_played_time = current_time
    
