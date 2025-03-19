import os
import threading
import wave
from datetime import datetime
from enum import Enum
from typing import Optional

import numpy as np
from pygame.mixer import Sound
from pygame.time import wait


class PlayerState(Enum):
    PLAYING = "playing"
    STOPPED = "stopped"
    STOPPING = "stopping"


class WavRecorder:
    def __init__(
        self,
        channel_bit_depth: int,
        channel_frame_rate: int,
        channel_count: int,
        filename: str,
    ):
        self.channel_bit_depth = channel_bit_depth
        self.channel_frame_rate = channel_frame_rate
        self.channel_count = channel_count
        self.filename = filename
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def record(self, sound: Sound) -> None:
        frames = sound.get_raw()
        if os.path.exists(self.filename):
            with wave.open(self.filename, "rb") as file:
                frames = file.readframes(file.getnframes()) + frames

        with wave.open(self.filename, "wb") as file:
            file.setnchannels(self.channel_count)
            file.setsampwidth(self.channel_bit_depth)
            file.setframerate(self.channel_frame_rate)
            file.writeframes(frames)


class LoopPlayer:
    """
    Loop player repeats a sound indefinitely until it is stopped
    """

    def __init__(
        self,
        sound: Optional[Sound] = None,
        recorder: Optional[WavRecorder] = None,
    ):
        self.__state = PlayerState.STOPPED
        self.__thread = None
        self.__sound = sound
        self.__recorder = recorder
        self.__crossfade_percentage = 0.02  # 2% of sound length for crossfade
        self.__crossfaded_sound = None

    def start(self):
        self.__thread = threading.Thread(name="loop-player", target=self.__start)
        self.__thread.start()

    def __create_crossfaded_sound(self, sound_data: bytes) -> Sound:
        """Create a crossfaded version of the sound."""
        sound_length = len(sound_data)
        crossfade_samples = int(sound_length * self.__crossfade_percentage)

        # Ensure minimum and maximum crossfade lengths
        min_crossfade = 500  # Minimum 11ms at 44.1kHz
        max_crossfade = 4000  # Maximum 91ms at 44.1kHz
        crossfade_samples = max(min_crossfade, min(crossfade_samples, max_crossfade))

        if sound_length <= crossfade_samples * 2:
            return Sound(buffer=sound_data)

        # Convert bytes to samples (assuming 16-bit audio) and create a copy
        samples = np.frombuffer(sound_data, dtype=np.int16).copy()

        # Create fade-in and fade-out curves with smoother transition
        fade_in = np.sin(np.linspace(0, np.pi / 2, crossfade_samples)) ** 2
        fade_out = np.sin(np.linspace(np.pi / 2, np.pi, crossfade_samples)) ** 2

        # Apply crossfade
        samples[:crossfade_samples] = (samples[:crossfade_samples] * fade_in).astype(
            np.int16
        )
        samples[-crossfade_samples:] = (samples[-crossfade_samples:] * fade_out).astype(
            np.int16
        )

        # Convert back to bytes
        crossfade_buffer = samples.tobytes()
        return Sound(buffer=crossfade_buffer)

    def __start(self):
        self.__state = PlayerState.PLAYING

        # Pre-create the crossfaded sound
        if self.__sound is not None:
            self.__crossfaded_sound = self.__create_crossfaded_sound(
                self.__sound.get_raw()
            )

        while self.__state == PlayerState.PLAYING:
            if self.__sound is None:
                wait(100)
                continue

            start_time = datetime.now()

            # Play the pre-created crossfaded sound
            if self.__crossfaded_sound is not None:
                self.__crossfaded_sound.play()

            if self.__recorder is not None:
                self.__recorder.record(self.__sound)

            end_time = datetime.now()
            processing_time = (end_time - start_time).microseconds // 1000
            wait_time = int(self.__sound.get_length() * 1000) - processing_time
            wait(wait_time)

        self.__state = PlayerState.STOPPED

    def stop(self):
        self.__state = PlayerState.STOPPING
        if self.__thread is not None:
            self.__thread.join()

    def set_sound(self, sound: Sound):
        self.__sound = sound
        # Recreate the crossfaded sound when setting a new sound
        self.__crossfaded_sound = self.__create_crossfaded_sound(sound.get_raw())
