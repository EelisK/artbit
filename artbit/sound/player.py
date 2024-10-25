import threading
from enum import Enum
from typing import Optional

from pygame.mixer import Sound
from pygame.time import wait


class PlayerState(Enum):
    PLAYING = "playing"
    STOPPED = "stopped"
    STOPPING = "stopping"


class LoopPlayer:
    """
    Loop player repeats a sound indefinitely until it is stopped
    """

    def __init__(self, sound: Optional[Sound] = None):
        self.__state = PlayerState.STOPPED
        self.__thread = None
        self.__sound = sound

    def start(self):
        self.__thread = threading.Thread(name="loop-player", target=self.start_player)
        self.__thread.start()

    def start_player(self):
        """
        Starts playing the generated heartbeat sound
        """
        self.__state = PlayerState.PLAYING
        while self.__state == PlayerState.PLAYING:
            if self.__sound is None:
                wait(100)
                continue

            self.__sound.play()
            wait(int(self.__sound.get_length() * 1000))

        self.__state = PlayerState.STOPPED

    def stop(self):
        """
        Stops the playback of the heartbeat sound

        NOTE: This method should be called from a different thread
        due to the blocking nature of the playback
        """
        self.__state = PlayerState.STOPPING
        if self.__thread is not None:
            self.__thread.join()

    def set_sound(self, sound: Sound):
        """
        Change the sound that is being looped
        """
        self.__sound = sound
