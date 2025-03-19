import numpy as np
import pygame
from numpy.typing import NDArray
from scipy import signal  # pyright: ignore[reportMissingTypeStubs]

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


class BrownNoise(ChannelAdapter):
    """
    Brown noise sound with a given duration
    """

    def __init__(self, duration: float) -> None:
        init_params = pygame.mixer.get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("Mixer is not initialized")

        channel_framerate, channel_bit_depth, channel_count = init_params

        white_noise = np.random.randn(round(duration * channel_framerate)).astype(
            np.float32
        )

        low_pass_filters: list[tuple[NDArray[np.float32], NDArray[np.float32]]] = []
        filter_order = 4
        frequency_bands_hz = [5, 10, 20, 40, 80, 160, 320]

        for freq in frequency_bands_hz:
            b, a = signal.butter(  # pyright: ignore
                filter_order, freq / (channel_framerate / 2), btype="low"
            )  # pyright: ignore
            low_pass_filters.append((b, a))  # pyright: ignore

        # Generate multiple layers of brown noise with different frequencies
        brown_noise_layers: list[NDArray[np.float32]] = []
        for b, a in low_pass_filters:
            filtered_noise: NDArray[np.float32] = np.convolve(  # pyright: ignore
                white_noise,
                np.ones(filter_order) / filter_order,
                mode="same",  # pyright: ignore
            )
            filtered_noise = signal.lfilter(b, a, filtered_noise)  # pyright: ignore
            brown_noise_layers.append(filtered_noise)

        # Combine the layers
        brown_noise = np.sum(np.vstack(brown_noise_layers), axis=0)

        super().__init__(channel_bit_depth, channel_count, brown_noise)


class WhiteNoise(ChannelAdapter):
    """
    White noise sound with a given duration
    """

    def __init__(self, duration: float) -> None:
        init_params = pygame.mixer.get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("Mixer is not initialized")

        channel_framerate, channel_bit_depth, channel_count = init_params

        white_noise = np.random.randn(round(duration * channel_framerate)).astype(
            np.float32
        )

        super().__init__(channel_bit_depth, channel_count, white_noise)


class LowPassFilter(ChannelAdapter):
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

        b, a = signal.butter(2, frequency / (channel_framerate / 2), btype="low")  # pyright: ignore
        low_pass_filtered = signal.lfilter(b, a, y_axis)  # pyright: ignore

        super().__init__(channel_bit_depth, channel_count, low_pass_filtered)  # pyright: ignore


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


class Silence(ChannelAdapter):
    """
    Sound of silence for a given duration

    """

    def __init__(self, duration: float) -> None:
        init_params = pygame.mixer.get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("Mixer is not initialized")

        channel_framerate, channel_bit_depth, channel_count = init_params
        super().__init__(
            channel_bit_depth,
            channel_count,
            np.zeros(round(duration * channel_framerate)).astype(np.float32),
        )


class FlatlineSound(ConstantFrequency):
    """
    The sound of flatlining in an ECG monitor, just for fun

    """

    ECG_FLATLINE_FREQUENCY = 996.75

    def __init__(self, duration: float) -> None:
        super().__init__(self.ECG_FLATLINE_FREQUENCY, duration)
