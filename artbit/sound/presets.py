import numpy as np
import pygame

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

        sound_duration_seconds = (bpm / 60.0) ** -1
        sound_sample_count = round(sound_duration_seconds * channel_framerate)

        x_axis = np.linspace(
            -sound_duration_seconds / 2,
            sound_duration_seconds / 2,
            sound_sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * self.HEARTBEAT_SOUND_FREQUENCY)

        # Apply dirac delta to the soundwave to simulate a heartbeat
        dirac_delta_limit = 0.09
        dirac_delta = np.power(
            np.e, -np.power((x_axis / sound_duration_seconds) / dirac_delta_limit, 2)
        ) / (dirac_delta_limit * np.sqrt(np.pi))
        smooth_dirac_delta = dirac_delta

        y_axis = y_axis * smooth_dirac_delta

        super().__init__(channel_bit_depth, channel_count, y_axis)


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
