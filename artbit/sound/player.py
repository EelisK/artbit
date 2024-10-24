import logging
import threading
from enum import Enum

import pygame

from artbit.sound.soundboard import Soundboard


class PlayerState(Enum):
    PLAYING = "playing"
    STOPPED = "stopped"
    STOPPING = "stopping"


class HeartbeatPlayer:
    """
    A class that generates and plays a heartbeat sound
    based on a given BPM value
    """

    def __init__(self, soundboard: Soundboard):
        self.__bpm = None
        self.__state = PlayerState.STOPPED
        self.__thread = None
        self.__soundboard = soundboard

    def play(self):
        self.__thread = threading.Thread(
            name="heartbeat-player", target=self.start_player
        )
        self.__thread.start()

    def start_player(self):
        """
        Starts playing the generated heartbeat sound
        """
        self.__state = PlayerState.PLAYING
        with self.__soundboard:
            while self.__state == PlayerState.PLAYING:
                if self.__bpm is None:
                    logging.info("No BPM set, waiting for a value")
                    pygame.time.wait(1000)
                    continue

                hearbeat_sound = self.__soundboard.heartbeat()
                hearbeat_sound.play()

                wait_time_ms = int(self.beat_interval_seconds * 1000)
                pygame.time.wait(wait_time_ms)

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

    def set_bpm(self, bpm: int):
        """
        Sets the BPM value for the heartbeat sound
        """
        self.__bpm = bpm
        self.beat_interval_seconds = (
            60.0 / self.__bpm - self.__soundboard.sound_duration
        )
