"""Module responsible for playing sound effects"""

from os.path import join
import pygame


class DummySound:
    """A fake sound object that silently catches and ignores audio calls during RL."""

    def play(self):
        pass

    def set_volume(self, volume):
        pass

    def stop(self):
        pass


class SoundManager:
    _sounds = {}
    _enabled = True
    _master_volume = 1.0

    @classmethod
    def init(cls, enable_audio=True):
        """Initializes the audio system. Pass False to disable entirely."""
        cls._enabled = enable_audio
        if cls._enabled:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

    @classmethod
    def load_all_sounds(cls):
        """Loads all game audio into RAM. Skips loading if audio is disabled."""
        if not cls._enabled:
            return

        sound_files = {
            "sword_hit_1": "sword_hit_1.wav",
            "sword_hit_2": "sword_hit_2.wav",
            "sword_hit_3": "sword_hit_3.wav",
            "sword_miss_1": "sword_miss_1.wav",
            "sword_miss_2": "sword_miss_2.wav",
            "sword_miss_3": "sword_miss_3.wav",
            "human_damage_1": "human_damage_1.wav",
            "human_damage_2": "human_damage_2.wav",
            "human_damage_3": "human_damage_3.wav",
            "block_1": "block_1.wav",
            "block_2": "block_2.wav",
            "block_3": "block_3.wav",
            "parry": "parry.wav",
            "parry_1": "parry_1.wav",
            "parry_2": "parry_2.wav",
            "parry_3": "parry_3.wav",
            "dodge": "dodge.wav",
            "break": "break.wav",
        }

        for name, filename in sound_files.items():
            path = join("assets", filename)
            try:
                cls._sounds[name] = pygame.mixer.Sound(path)
            except FileNotFoundError:
                print(f"Warning: Sound {filename} not found.")

    @classmethod
    def get_sound(cls, name):
        """Returns the sound object, or a dummy if audio is disabled/missing."""
        if not cls._enabled:
            return DummySound()

        return cls._sounds.get(name, DummySound())

    @classmethod
    def set_master_volume(cls, volume):
        """Sets the global volume. 'volume' must be between 0.0 and 1.0"""
        cls._master_volume = max(0.0, min(1.0, float(volume)))

        if not cls._enabled:
            return

        # Instantly update all currently loaded sounds
        for sound in cls._sounds.values():
            sound.set_volume(cls._master_volume)
