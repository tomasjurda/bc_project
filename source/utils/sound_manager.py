"""Module responsible for playing sound effects"""

import pygame


class SoundManager:
    last_played_time = 0
    volume = 0.4

    @staticmethod
    def play_sound(sound: pygame.mixer.Sound):
        current_time = pygame.time.get_ticks()
        if current_time - SoundManager.last_played_time <= 120:
            return

        sound.set_volume(SoundManager.volume)
        sound.play()
        SoundManager.last_played_time = current_time
