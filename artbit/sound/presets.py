import numpy as np
import pygame
from numpy.typing import NDArray

from artbit.sound.adapter import ChannelAdapter


class HeartbeatSound(ChannelAdapter):
    """
    Sound with sin-wave of given frequency
    """

    HEARTBEAT_SOUND_FREQUENCY: int = 70

    def __init__(self, bpm: int) -> None:
        init_params = pygame.mixer.get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("Mixer is not initialized")

        channel_framerate, channel_bit_depth, channel_count = init_params

        self.sound_duration = (bpm / 60.0) ** -1
        self.sample_count = round(self.sound_duration * channel_framerate)

        x_axis = np.linspace(
            -self.sound_duration / 2,
            self.sound_duration / 2,
            self.sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * self.HEARTBEAT_SOUND_FREQUENCY)

        delta = self.delta_laguerre()

        super().__init__(channel_bit_depth, channel_count, y_axis * delta)

    def delta_laguerre(self) -> NDArray[np.float32]:
        """
        Generate a delta using the Laguerre polynomials
        """
        delta_limit = 0.09
        laguerre_order = 10
        x = np.linspace(-1, 1, self.sample_count, dtype=np.float32, endpoint=False)
        return np.power(np.e, -np.power(x, 2) / delta_limit) * np.absolute(
            (np.polynomial.laguerre.lagval(2 * x / delta_limit, [0, laguerre_order]))  # pyright: ignore[reportUnknownArgumentType]
            / delta_limit
        )

    def delta_dirac(self) -> NDArray[np.float32]:
        """
        Generate a delta using the Dirac delta function
        """
        x = np.linspace(-1, 1, self.sample_count, dtype=np.float32, endpoint=False)
        delta_limit = 0.09
        delta = np.power(np.e, -np.power(x / self.sound_duration / delta_limit, 2)) / (
            delta_limit * np.sqrt(np.pi)
        )
        return delta


class ConstantFrequency(ChannelAdapter):
    """
    Sound with sin-wave of given frequency
    """

    def __init__(self, frequency: float, duration: float) -> None:
        init_params = pygame.mixer.get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("Mixer is not initialized")

        channel_framerate, channel_bit_depth, channel_count = init_params

        sound_sample_count = round(duration * channel_framerate)
        x_axis = np.linspace(
            0,
            duration,
            sound_sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * frequency)

        super().__init__(channel_bit_depth, channel_count, y_axis)


class FlatlineSound(ConstantFrequency):
    """
    The sound of flatlining in an ECG monitor, just for fun

    """

    ECG_FLATLINE_FREQUENCY = 996.75

    def __init__(self, duration: float) -> None:
        super().__init__(self.ECG_FLATLINE_FREQUENCY, duration)
