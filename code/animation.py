from settings import *

class Animation():
    def __init__(self, frames, speed, loop=False, loop_start_index=0):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.loop_start_index = loop_start_index
        
        self.frame_index = 0
        self.time_accumulator = 0
        self.finished = False
        self.last_frame_index = -1


    def reset(self):
        self.frame_index = 0
        self.time_accumulator = 0
        self.finished = False
        self.last_frame_index = -1


    def update(self, dt):
        if self.finished and not self.loop:
            return self.frames[-1]

        self.time_accumulator += dt
        
        # Uchováme si předchozí index pro detekci změny
        self.last_frame_index = int(self.frame_index)

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


    def get_current_image(self):
        return self.frames[int(self.frame_index)]


    def on_frame(self, target_frame):
        current = int(self.frame_index)
        return current == target_frame and current != self.last_frame_index

