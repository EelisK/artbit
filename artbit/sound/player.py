import os
import threading
import wave
from datetime import datetime
from enum import Enum
from typing import Optional

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

    def start(self):
        self.__thread = threading.Thread(name="loop-player", target=self.__start)
        self.__thread.start()

    def __start(self):
        self.__state = PlayerState.PLAYING
        while self.__state == PlayerState.PLAYING:
            if self.__sound is None:
                wait(100)
                continue

            start_time = datetime.now()
            self.__sound.play()
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
