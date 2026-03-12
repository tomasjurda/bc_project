"""
Module providing the Animation class used to handle sprite framing,
looping, and play speeds based on delta time.
"""

import pygame


class Animation:
    """
    Manages a sequence of pygame surfaces (frames) to create an animation.

    Attributes:
        frames (list[pygame.Surface]): The list of image frames to cycle through.
        speed (float): The speed at which frames play (frames per second).
        loop (bool): Whether the animation restarts after finishing.
        loop_start_index (int): The index to return to when looping (allows intro frames).
        frame_index (float): The current active frame index.
        time_accumulator (float): Tracks accumulated delta time to trigger frame changes.
        finished (bool): Flag indicating if the animation has completed.
        last_frame_index (int): Tracks the previous frame to detect transition moments.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        speed: float,
        loop: bool = False,
        loop_start_index: int = 0,
    ) -> None:
        """
        Initializes the Animation sequence.

        Args:
            frames (list[pygame.Surface]): List of frame images.
            speed (float): Playback speed (frames per second).
            loop (bool): If True, loops back to loop_start_index when done.
            loop_start_index (int): The frame index to loop back to.
        """
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.loop_start_index = loop_start_index

        self.frame_index = 0
        self.time_accumulator = 0
        self.finished = False
        self.last_frame_index = -1

    def reset(self) -> None:
        """Resets the animation back to its starting state."""
        self.frame_index = 0
        self.time_accumulator = 0
        self.finished = False
        self.last_frame_index = -1

    def update(self, dt: float) -> pygame.Surface:
        """
        Advances the animation based on the elapsed delta time.

        Args:
            dt (float): Delta time (time elapsed since the last frame).

        Returns:
            pygame.Surface: The current frame's image surface.
        """

        if self.finished and not self.loop:
            return self.frames[-1]

        self.time_accumulator += dt

        # Store the previous integer index for transition detection
        self.last_frame_index = int(self.frame_index)

        # Check if enough time has passed to advance the frame
        if self.time_accumulator >= 1 / self.speed:
            self.time_accumulator = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = self.loop_start_index
                else:
                    self.frame_index = len(self.frames) - 1
                    self.finished = True

        return self.frames[int(self.frame_index)]

    def get_current_image(self) -> pygame.Surface:
        """
        Fetches the current frame without advancing the animation time.

        Returns:
            pygame.Surface: The active image surface.
        """
        return self.frames[int(self.frame_index)]

    def on_frame(self, target_frame: int) -> bool:
        """
        Checks if the animation *just* transitioned onto a specific frame index
        during the current update cycle. Useful for triggering sound effects or hitboxes.

        Args:
            target_frame (int): The integer index of the frame to check for.

        Returns:
            bool: True if the animation just reached the target frame this tick.
        """
        current = int(self.frame_index)
        return current == target_frame and current != self.last_frame_index
