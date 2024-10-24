from typing import Any

import pygame
from numpy import int16, linspace, pi, sin, zeros
from numpy.typing import NDArray
from pygame.mixer import Sound


class Soundboard:
    def __init__(self):
        self.sound_sample_rate: int = 44100
        self.num_channels: int = 2
        self.sound_duration: float = 0.1
        # Normal heart rate frequency is 20-200 Hz
        self.sound_frequency: int = 70

    def __enter__(self):
        pygame.mixer.init(self.sound_sample_rate, channels=self.num_channels)
        return self

    def __exit__(self, exc_type: type[Exception], exc_val: Exception, exc_tb: Any):
        pygame.mixer.quit()

    def heartbeat(self) -> Sound:
        num_samples = int(self.sound_duration * self.sound_sample_rate)
        t = linspace(0, self.sound_duration, num_samples, endpoint=False)
        data = zeros((num_samples, self.num_channels), dtype=int16)
        channel_data = 32767 * sin(2 * pi * self.sound_frequency * t)
        for i in range(self.num_channels):
            data[:, i] = channel_data
        return self.make_sound(data)

    def make_sound(self, data: NDArray[int16]) -> Sound:
        return pygame.sndarray.make_sound(data)
