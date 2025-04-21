import logging

import numpy as np
from numpy.typing import NDArray
from pygame.mixer import Sound
from pygame.mixer import get_init as mixer_get_init
from pygame.mixer import init as mixer_init

from app.singleton import SingletonMeta

logger = logging.getLogger(__name__)


class ChannelParam(metaclass=SingletonMeta):
    """
    Singleton class for channel parameters
    """

    def __init__(self) -> None:
        init_params = mixer_get_init()
        if init_params is None:  # pyright: ignore[reportUnnecessaryComparison]
            logger.info("Initializing the mixer with default parameters")
            mixer_init()
            init_params = mixer_get_init()

        self.__channel_framerate, self.__channel_bit_depth, self.__channel_count = (
            init_params
        )

    @property
    def framerate(self) -> int:
        return self.__channel_framerate

    @property
    def bit_depth(self) -> int:
        return self.__channel_bit_depth

    @property
    def count(self) -> int:
        return self.__channel_count


class ChannelAdapter(Sound):
    """
    Sound adapter for pygame.mixer.Sound
    using numpy arrays for soundwave data
    """

    channel_param: ChannelParam = ChannelParam()

    def __init__(self, wave: NDArray[np.float32]) -> None:
        # Resolve the appropriate data type for the bit depth
        bit_depth_type_map = {
            8: np.uint8,
            -8: np.int8,
            16: np.uint16,
            -16: np.int16,
            32: np.uint32,
            -32: np.int32,
        }
        if self.channel_param.bit_depth not in bit_depth_type_map:
            raise ValueError("Unsupported bit depth")

        self.dtype = bit_depth_type_map[self.channel_param.bit_depth]

        # Normalize the soundwave if it is not empty
        if not np.all(wave == 0):
            wave = self.normalize(wave)

        self.wave = wave

        # Extend the soundwave to the channel count
        data = np.zeros(
            (len(wave), self.channel_param.count),
            dtype=bit_depth_type_map[self.channel_param.bit_depth],
        )
        for i in range(self.channel_param.count):
            data[:, i] = self.wave

        return super().__init__(data)

    def normalize(self, wave: NDArray[np.float32]) -> NDArray[np.float32]:
        """
        Normalize the soundwave to the bit depth
        """
        max_bitrate = (1 << (abs(self.channel_param.bit_depth) - 1)) - 1
        if self.channel_param.bit_depth < 0:
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

    def __add__(self, other: "ChannelAdapter") -> "ChannelAdapter":
        return self.add(other)

    def __mul__(self, other: "ChannelAdapter") -> "ChannelAdapter":
        return self.mul(other)

    def __or__(self, other: "ChannelAdapter") -> "ChannelAdapter":
        return self.concat(other)

    def add(self, other: "ChannelAdapter") -> "ChannelAdapter":
        """
        Add two ChannelAdapter instances
        """
        return ChannelAdapter(self.wave + other.wave)

    def mul(self, other: "ChannelAdapter") -> "ChannelAdapter":
        """
        Multiply two ChannelAdapter instances
        """
        return ChannelAdapter(self.wave * other.wave)

    def concat(self, other: "ChannelAdapter") -> "ChannelAdapter":
        """
        Concatenate two ChannelAdapter instances
        """
        return ChannelAdapter(np.concatenate((self.wave, other.wave)))
