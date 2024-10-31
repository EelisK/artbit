import numpy as np
from numpy.typing import NDArray
from pygame.mixer import Sound


class ChannelAdapter(Sound):
    """
    Sound adapter for pygame.mixer.Sound
    using numpy arrays for soundwave data
    """

    def __init__(
        self, channel_bit_depth: int, channel_count: int, wave: NDArray[np.float32]
    ) -> None:
        # Resolve the appropriate data type for the bit depth
        bit_depth_type_map = {
            8: np.uint8,
            -8: np.int8,
            16: np.uint16,
            -16: np.int16,
            32: np.uint32,
            -32: np.int32,
        }
        if channel_bit_depth not in bit_depth_type_map:
            raise ValueError("Unsupported bit depth")

        self.channel_bit_depth = channel_bit_depth
        self.channel_count = channel_count
        self.dtype = bit_depth_type_map[channel_bit_depth]

        # Normalize the soundwave if it is not empty
        if np.all(wave == 0):
            self.wave = wave
        else:
            self.wave = self.normalize(wave)

        # Extend the soundwave to the channel count
        data = np.zeros(
            (len(wave), channel_count),
            dtype=bit_depth_type_map[channel_bit_depth],
        )
        for i in range(channel_count):
            data[:, i] = self.wave

        super().__init__(data)

    def normalize(self, wave: NDArray[np.float32]) -> NDArray[np.float32]:
        """
        Normalize the soundwave to the bit depth
        """
        max_bitrate = (1 << (abs(self.channel_bit_depth) - 1)) - 1
        if self.channel_bit_depth < 0:
            return self.normalize_range(wave, -max_bitrate, max_bitrate)

        return self.normalize_range(wave, 0, max_bitrate)

    def normalize_range(
        self, wave: NDArray[np.float32], min: float, max: float
    ) -> NDArray[np.float32]:
        """
        Normalize the soundwave to the range [min, max]
        """
        diff = max - min
        return (wave - np.min(wave)) / np.ptp(wave) * diff + min
