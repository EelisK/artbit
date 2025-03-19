import numpy as np
from numpy.typing import NDArray
from scipy import signal  # pyright: ignore[reportMissingTypeStubs]

from artbit.sound.adapter import ChannelAdapter


class CompositeSound(ChannelAdapter):
    def __init__(self, sounds: list[ChannelAdapter]) -> None:
        # Find the longest sound in the list
        max_duration = max([sound.get_length() for sound in sounds])

        # Generate a composite sound by mixing all sounds
        composite_wave = np.zeros(
            round(max_duration * self.channel_param.framerate), dtype=np.float32
        )
        for sound in sounds:
            sound_wave = sound.wave
            sound_wave = sound_wave[: len(composite_wave)]
            composite_wave += sound_wave

        super().__init__(composite_wave)


class GaussianPulse(ChannelAdapter):
    """
    Generates a Gaussian pulse waveform
    """

    def __init__(self, length: int, sigma: float, amplitude: float = 1.0) -> None:
        """Create a Gaussian pulse.

        Args:
            length: Length of the pulse in samples
            sigma: Standard deviation of the Gaussian
            amplitude: Maximum amplitude of the pulse
        """
        x = np.linspace(-length // 2, length // 2, length, dtype=np.float32)
        pulse = amplitude * np.exp(-(x**2) / (2 * sigma**2))
        super().__init__(pulse)


class DeepBrownNoise(ChannelAdapter):
    """
    Generates deep brown noise with emphasis on low frequencies
    """

    def __init__(self, length: int) -> None:
        """Create deep brown noise.

        Args:
            length: Length of the noise in samples
            sample_rate: Sample rate in Hz
        """
        # White noise
        white_noise: NDArray[np.float32] = np.random.normal(0, 1, length).astype(
            np.float32
        )

        # Create brown noise by integrating white noise with stronger coefficient
        brown: NDArray[np.float32] = np.zeros_like(white_noise)
        brown[0] = white_noise[0]
        for i in range(1, length):
            # Higher coefficient (0.98) gives more emphasis to low frequencies
            brown[i] = 0.98 * brown[i - 1] + white_noise[i] * 0.1

        # Apply a low-pass filter to further emphasize bass
        b, a = signal.butter(  # pyright: ignore
            3, 150.0 / (self.channel_param.framerate / 2), btype="low"
        )  # pyright: ignore
        filtered_brown: NDArray[np.float32] = signal.filtfilt(b, a, brown)  # pyright: ignore

        # Normalize
        filtered_brown = filtered_brown / np.max(np.abs(filtered_brown))  # pyright: ignore
        super().__init__(filtered_brown)  # pyright: ignore


class HeartbeatSoundComponent(ChannelAdapter):
    """Base class for heartbeat sound components."""

    def __init__(self, bpm: int) -> None:
        """Initialize with BPM.

        Args:
            bpm: Beats per minute
        """
        self.beat_period = 60.0 / bpm
        self.sample_count = round(self.beat_period * self.channel_param.framerate)
        super().__init__(np.zeros(self.sample_count, dtype=np.float32))


class LubSound(HeartbeatSoundComponent):
    """Generates the 'lub' sound component."""

    def __init__(self, bpm: int) -> None:
        """Create the lub sound.

        Args:
            bpm: Beats per minute
        """
        super().__init__(bpm)

        # Generate the lub sound (S1) - sharper and louder
        lub_width = int(0.07 * self.sample_count)
        lub_pulse = GaussianPulse(2 * lub_width, sigma=lub_width / 3)
        lub_peak = lub_pulse.wave / np.max(lub_pulse.wave)

        # Position the sound in the beat period
        lub_pos = int(0.2 * self.sample_count)

        # Add lub sound to the waveform
        for i in range(len(lub_peak)):
            pos = (lub_pos - lub_width + i) % self.sample_count
            self.wave[pos] = max(self.wave[pos], lub_peak[i])

        # Apply envelope shaping
        self.wave = self.wave**2  # Square for more pronounced curve


class DubSound(HeartbeatSoundComponent):
    """Generates the 'dub' sound component."""

    def __init__(self, bpm: int) -> None:
        """Create the dub sound.

        Args:
            bpm: Beats per minute
        """
        super().__init__(bpm)

        # Generate the dub sound (S2) - softer and shorter
        dub_width = int(0.05 * self.sample_count)
        dub_pulse = GaussianPulse(2 * dub_width, sigma=dub_width / 3)
        dub_peak = 0.6 * dub_pulse.wave / np.max(dub_pulse.wave)  # Smaller than S1

        # Position the sound in the beat period
        dub_pos = int(0.55 * self.sample_count)

        # Add dub sound to the waveform
        for i in range(len(dub_peak)):
            pos = (dub_pos - dub_width + i) % self.sample_count
            self.wave[pos] = max(self.wave[pos], dub_peak[i])

        # Apply envelope shaping
        self.wave = self.wave**2  # Square for more pronounced curve


class RealisticHeartbeatSound(ChannelAdapter):
    """
    A hyper-realistic heartbeat sound generator that creates the characteristic "lub-dub" sound.
    Uses Gaussian pulses for the main sounds and deep brown noise for added realism.
    """

    def __init__(self, bpm: int) -> None:
        # Calculate the beat period and sample count
        beat_period = 60.0 / bpm
        sample_count = round(beat_period * self.channel_param.framerate)

        # Generate the main sound components
        lub_sound = LubSound(bpm)
        dub_sound = DubSound(bpm)
        brown_noise = DeepBrownNoise(sample_count)

        # Combine the sounds
        combined_sound = lub_sound.wave + dub_sound.wave
        combined_sound = combined_sound * brown_noise.wave

        # Normalize the sound
        combined_sound = combined_sound / np.max(np.abs(combined_sound))

        super().__init__(combined_sound)


class BrownNoise(ChannelAdapter):
    """
    Brown noise sound with a given duration
    """

    def __init__(self, duration: float) -> None:
        white_noise = np.random.randn(
            round(duration * self.channel_param.framerate)
        ).astype(np.float32)

        low_pass_filters: list[tuple[NDArray[np.float32], NDArray[np.float32]]] = []
        filter_order = 4
        frequency_bands_hz = [5, 10, 20, 40, 80, 160, 320]
        frequency_amplitudes = [1, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625]

        for freq in frequency_bands_hz:
            b, a = signal.butter(  # pyright: ignore
                filter_order, freq / (self.channel_param.framerate / 2), btype="low"
            )  # pyright: ignore
            low_pass_filters.append((b, a))  # pyright: ignore

        for i, (b, a) in enumerate(low_pass_filters):
            b = b * frequency_amplitudes[i]
            a = a * frequency_amplitudes[i]
            low_pass_filters[i] = (b, a)

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

        super().__init__(brown_noise)


class WhiteNoise(ChannelAdapter):
    """
    White noise sound with a given duration
    """

    def __init__(self, duration: float) -> None:
        white_noise = np.random.randn(
            round(duration * self.channel_param.framerate)
        ).astype(np.float32)

        super().__init__(white_noise)


class LowPassFilter(ChannelAdapter):
    """
    Sound with sin-wave of given frequency
    """

    def __init__(self, frequency: float, duration: float) -> None:
        sound_sample_count = round(duration * self.channel_param.framerate)
        x_axis = np.linspace(
            0,
            duration,
            sound_sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * frequency)

        b, a = signal.butter(  # pyright: ignore
            2, frequency / (self.channel_param.framerate / 2), btype="low"
        )
        low_pass_filtered: NDArray[np.float32] = signal.lfilter(b, a, y_axis)  # pyright: ignore

        super().__init__(low_pass_filtered)


class ConstantFrequency(ChannelAdapter):
    """
    Sound with sin-wave of given frequency
    """

    def __init__(self, frequency: float, duration: float) -> None:
        sound_sample_count = round(duration * self.channel_param.framerate)
        x_axis = np.linspace(
            0,
            duration,
            sound_sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * frequency)

        super().__init__(y_axis)


class Silence(ChannelAdapter):
    """
    Sound of silence for a given duration

    """

    def __init__(self, duration: float) -> None:
        super().__init__(
            np.zeros(round(duration * self.channel_param.framerate)).astype(np.float32),
        )


class FlatlineSound(ConstantFrequency):
    """
    The sound of flatlining in an ECG monitor, just for fun

    """

    ECG_FLATLINE_FREQUENCY = 996.75

    def __init__(self, duration: float) -> None:
        super().__init__(self.ECG_FLATLINE_FREQUENCY, duration)
