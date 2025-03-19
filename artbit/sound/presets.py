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


class HB(ChannelAdapter):
    def __init__(self, bpm: int) -> None:
        sound_duration = (bpm / 60.0) ** -1

        lub_duration = 0.12 * sound_duration
        dub_duration = 0.1 * sound_duration
        remainder_duration = sound_duration - lub_duration - dub_duration

        lub = LowPassFilter(100, lub_duration)
        dub = LowPassFilter(50, dub_duration)
        remainder = Silence(remainder_duration)
        brown_noise = BrownNoise(sound_duration)

        composite = (lub | dub | remainder) * brown_noise

        super().__init__(composite.wave)


class HeartbeatSound(ChannelAdapter):
    """
    Sound with sin-wave of given frequency
    """

    HEARTBEAT_SOUND_FREQUENCY: int = 70

    def __init__(self, bpm: int) -> None:
        self.sound_duration = (bpm / 60.0) ** -1
        self.sample_count = round(self.sound_duration * self.channel_param.framerate)

        x_axis = np.linspace(
            -self.sound_duration / 2,
            self.sound_duration / 2,
            self.sample_count,
            dtype=np.float32,
            endpoint=False,
        )
        y_axis = np.sin(2 * np.pi * x_axis * self.HEARTBEAT_SOUND_FREQUENCY)

        delta = self.delta_laguerre()

        super().__init__(y_axis * delta)

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
        white_noise = np.random.randn(
            round(duration * self.channel_param.framerate)
        ).astype(np.float32)

        low_pass_filters: list[tuple[NDArray[np.float32], NDArray[np.float32]]] = []
        filter_order = 4
        frequency_bands_hz = [5, 10, 20, 40, 80, 160, 320]

        for freq in frequency_bands_hz:
            b, a = signal.butter(  # pyright: ignore
                filter_order, freq / (self.channel_param.framerate / 2), btype="low"
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


class RealisticHeartbeatSound(ChannelAdapter):
    """
    A realistic heartbeat sound that combines both the heartbeat waveform and brown noise
    for added realism. Uses Gaussian pulses to create the characteristic "lub-dub" sound.
    """

    def __init__(self, bpm: int, frequency: float = 50.0) -> None:
        # Use provided frequency or fall back to default
        # Lower values (30-50) give deeper, more bassy heartbeats
        # Higher values (70-100) give sharper, more pronounced heartbeats
        self.frequency = frequency

        # Calculate duration and samples based on BPM
        duration = (bpm / 60.0) ** -1  # Duration of one heartbeat in seconds
        sample_count = round(duration * self.channel_param.framerate)

        # Create the heartbeat waveform
        heartbeat = self._generate_heartbeat(sample_count)

        # Generate and mix in brown noise
        noise = self._generate_brown_noise(sample_count)

        # Apply fade in/out to both components to ensure smooth transitions
        fade_samples = int(0.05 * sample_count)  # 5% fade at start and end
        fade_in = np.linspace(0, 1, fade_samples, dtype=np.float32)
        fade_out = np.linspace(1, 0, fade_samples, dtype=np.float32)
        fade_envelope = np.ones(sample_count, dtype=np.float32)
        fade_envelope[:fade_samples] = fade_in
        fade_envelope[-fade_samples:] = fade_out

        # Smooth the envelope
        fade_envelope = signal.savgol_filter(fade_envelope, 11, 2)  # pyright: ignore[reportUnknownVariableType]

        # Apply fade to both components
        heartbeat *= fade_envelope
        noise *= fade_envelope

        # Combine heartbeat and noise with adjusted mix ratio
        wave = heartbeat * 0.999 + noise * 0.001

        # Apply gentle compression instead of hard clipping
        wave = self._compress_audio(wave, threshold=0.7, ratio=3.0)

        super().__init__(wave)

    def _generate_heartbeat(self, sample_count: int) -> NDArray[np.float32]:
        """Generate the main heartbeat waveform with lub-dub sounds."""
        period_samples = sample_count

        # Adjust widths based on frequency - higher frequencies need narrower pulses
        base_width_factor = 50.0 / self.frequency  # Scale width relative to 50Hz
        s1_width = int(
            0.12 * period_samples * base_width_factor
        )  # Wider for smoother transition
        s2_width = int(
            0.1 * period_samples * base_width_factor
        )  # Wider for smoother transition

        # Generate Gaussian pulses with slopes adjusted for frequency
        sigma_factor = np.sqrt(50.0 / self.frequency)  # Adjust sigma based on frequency
        s1_peak = self._gaussian_pulse(
            2 * s1_width, s1_width / (3 * sigma_factor), amplitude=1.2
        )
        s1_peak = s1_peak / np.max(s1_peak)

        s2_peak = self._gaussian_pulse(
            2 * s2_width, s2_width / (3 * sigma_factor), amplitude=1.0
        )
        s2_peak = 0.7 * s2_peak / np.max(s2_peak)

        # Create the full waveform
        wave = np.zeros(sample_count, dtype=np.float32)

        # Position the lub sound at 20% of the cycle
        s1_pos = int(0.2 * period_samples)
        s1_start = max(0, s1_pos - s1_width)
        s1_end = min(sample_count, s1_pos + s1_width)
        if s1_end > s1_start:
            # Apply smooth window to avoid discontinuities
            window = np.hanning(s1_end - s1_start)
            wave[s1_start:s1_end] = s1_peak[: (s1_end - s1_start)] * window

        # Position the dub sound at 55% of the cycle
        s2_pos = int(0.55 * period_samples)
        s2_start = max(0, s2_pos - s2_width)
        s2_end = min(sample_count, s2_pos + s2_width)
        if s2_end > s2_start:
            # Apply smooth window to avoid discontinuities
            window = np.hanning(s2_end - s2_start)
            wave[s2_start:s2_end] = s2_peak[: (s2_end - s2_start)] * window

        # Apply gentler shaping for punch without introducing artifacts
        # Scale the input to tanh based on frequency to maintain consistent "punchiness"
        drive = 2.0 * np.sqrt(
            self.frequency / 50.0
        )  # More drive for higher frequencies
        wave = np.tanh(wave * drive) * 0.7  # Soft clipping instead of hard squaring

        return wave

    def _gaussian_pulse(
        self, length: int, sigma: float, amplitude: float = 1.0
    ) -> NDArray[np.float32]:
        """Generate a Gaussian pulse for heart sounds."""
        x = np.linspace(-length // 2, length // 2, length, dtype=np.float32)
        pulse = amplitude * np.exp(-(x**2) / (2 * sigma**2))
        return pulse.astype(np.float32)

    def _generate_brown_noise(self, length: int) -> NDArray[np.float32]:
        """Generate deep brown noise with emphasis on low frequencies."""
        # Generate white noise
        white = np.random.normal(0, 1, length).astype(np.float32)

        # Create brown noise through integration with gentler coefficients
        brown = np.zeros(length, dtype=np.float32)
        brown[0] = white[0]
        for i in range(1, length):
            brown[i] = 0.99 * brown[i - 1] + white[i] * 0.05  # Gentler coefficients

        # Apply low-pass filter with cutoff scaled to match heartbeat frequency
        cutoff = min(self.frequency * 1.6, 80)  # Scale cutoff with frequency, max 80Hz
        b, a = signal.butter(2, cutoff / (length / 2), "low")  # pyright: ignore[reportUnknownVariableType]
        filtered = signal.filtfilt(b, a, brown)  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]

        # Normalize more gently
        filtered = filtered / (np.max(np.abs(filtered)) + 1e-6)  # pyright: ignore
        # Soft limiting
        filtered = np.tanh(filtered * 1.2) * 0.7  # pyright: ignore

        return filtered.astype(np.float32)

    def _compress_audio(
        self, wave: NDArray[np.float32], threshold: float = 0.7, ratio: float = 3.0
    ) -> NDArray[np.float32]:
        """Apply gentle compression to avoid sudden transitions."""
        # Calculate the amount of gain reduction needed
        gain_mask = np.abs(wave) > threshold
        gain_reduction = np.zeros_like(wave)
        gain_reduction[gain_mask] = (np.abs(wave[gain_mask]) - threshold) * (
            1 - 1 / ratio
        )

        # Apply compression
        compressed = np.copy(wave)
        compressed[gain_mask] *= 1 - gain_reduction[gain_mask]

        # Apply makeup gain
        makeup_gain = 1.0 / (1.0 - (1.0 - 1.0 / ratio) * (1.0 - threshold))
        compressed *= makeup_gain * 0.95  # Slight safety margin

        return compressed
