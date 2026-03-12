"""Module responsible for managing, caching, and playing sound effects."""

from os.path import join
import pygame


class DummySound:
    """
    A fake sound object that silently catches and ignores audio calls.
    Used during headless Reinforcement Learning training or when audio is disabled
    to prevent game crashes when entities try to play() missing sounds.
    """

    def play(self):
        """Silently ignores the play request."""

    def set_volume(self, volume: float):
        """Silently ignores the volume adjustment request."""

    def stop(self):
        """Silently ignores the stop request."""


class SoundManager:
    """
    A static manager class for loading, caching, and globally controlling audio.
    """

    _sounds = {}
    _enabled = True
    _master_volume = 1.0

    @classmethod
    def init(cls, enable_audio: bool = True) -> None:
        """
        Initializes the audio system. Pass False to disable entirely.

        Args:
            enable_audio (bool): If True, initializes the pygame mixer. If False,
                audio is completely skipped (useful for headless RL training).
        """
        cls._enabled = enable_audio
        if cls._enabled:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

    @classmethod
    def load_all_sounds(cls):
        """
        Loads all game audio into RAM from the disk.
        Skips loading if audio is disabled.
        """
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

        # Iterate through the dictionary and attempt to load each sound file
        for name, filename in sound_files.items():
            path = join("assets", filename)
            try:
                cls._sounds[name] = pygame.mixer.Sound(path)
            except FileNotFoundError:
                print(f"Warning: Sound {filename} not found.")

    @classmethod
    def get_sound(cls, name: str) -> pygame.mixer.Sound | DummySound:
        """
        Returns the sound object by its name key.
        Returns a DummySound if audio is disabled or if the file was not found.

        Args:
            name (str): The string identifier key for the sound.

        Returns:
            pygame.mixer.Sound | DummySound: The requested sound or a safe dummy.
        """
        if not cls._enabled:
            return DummySound()

        return cls._sounds.get(name, DummySound())

    @classmethod
    def set_master_volume(cls, volume: float) -> None:
        """
        Sets the global master volume for all currently loaded sounds.

        Args:
            volume (float): The desired volume level (clamped between 0.0 and 1.0).
        """

        cls._master_volume = pygame.math.clamp(volume, 0.0, 1.0)

        if not cls._enabled:
            return

        # Instantly apply the updated volume to all cached sounds
        for sound in cls._sounds.values():
            sound.set_volume(cls._master_volume)
