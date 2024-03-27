import json
import pygame
import logging
import threading
import numpy as np

from enum import Enum
from pika.adapters.blocking_connection import BlockingChannel as ControlChannel
from shared import schemas
from shared.rmq import channel as rmq_channel

logging.basicConfig(
    level=logging.INFO,
    format="(%(threadName)-9s) %(message)s",
)


class PlayerState(Enum):
    PLAYING = "playing"
    STOPPED = "stopped"
    STOPPING = "stopping"


class HeartbeatPlayer:
    """
    A class that generates and plays a heartbeat sound
    based on a given BPM value
    """

    def __init__(self):
        self.sound_sample_rate = 44100
        self.sound_duration = 0.1
        # Normal heart rate frequency is 20-200 Hz
        self.sound_frequency = 70
        self.__bpm = None
        self.__state = PlayerState.STOPPED
        self.__thread = None

    def play(self):
        self.__thread = threading.Thread(
            name="heartbeat-player", target=self.start_player
        )
        self.__thread.start()

    def start_player(self):
        """
        Starts playing the generated heartbeat sound
        """
        pygame.mixer.init(self.sound_sample_rate, channels=2)
        self.__state = PlayerState.PLAYING
        while self.__state == PlayerState.PLAYING:
            if self.__bpm is None:
                logging.info("No BPM set, waiting for a value")
                pygame.time.wait(1000)
                continue
            self.play_beat()
        pygame.mixer.quit()
        self.__state = PlayerState.STOPPED

    def play_beat(self):
        """
        Plays a single beat of the heartbeat sound
        """
        hearbeat_sound = self.__get_sound()
        hearbeat_sound.play()
        pygame.time.wait(int(self.beat_interval_seconds * 1000))  # in milliseconds

    def stop(self):
        """
        Stops the playback of the heartbeat sound

        NOTE: This method should be called from a different thread
        due to the blocking nature of the playback
        """
        self.__state = PlayerState.STOPPING
        if self.__thread is not None:
            self.__thread.join()

    def set_bpm(self, bpm):
        """
        Sets the BPM value for the heartbeat sound
        """
        self.__bpm = bpm
        self.beat_interval_seconds = 60.0 / self.__bpm - self.sound_duration

    def __get_sound(self):
        num_samples = int(self.sound_duration * self.sound_sample_rate)
        t = np.linspace(0, self.sound_duration, num_samples, endpoint=False)
        data = np.zeros((num_samples, 2), dtype=np.int16)
        data[:, 0] = 32767 * np.sin(2 * np.pi * self.sound_frequency * t)
        data[:, 1] = 32767 * np.sin(2 * np.pi * self.sound_frequency * t)
        return pygame.sndarray.make_sound(data)


class HeartbeatConsumer:
    """
    A class that controls the playback of HeartbeatPlayers
    based on received heart rate data
    """

    players: list[HeartbeatPlayer]

    def __init__(self, control_channel: ControlChannel):
        self.control_channel = control_channel
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def start(self):
        """
        Starts the player and the control loop
        """
        for player in self.players:
            player.play()
        self.__start_consumer()

    def stop(self):
        """
        Stops the player and the control loop
        """
        self.__stop_consumer()
        for player in self.players:
            player.stop()

    def __start_consumer(self):
        for method_frame, _, body in self.control_channel.consume("heartbeats"):
            self.control_channel.basic_ack(method_frame.delivery_tag)

            hearbeat_data: schemas.Heartbeat = json.loads(body)
            if hearbeat_data["is_error"]:
                logging.warning(
                    "Error in heartbeat data: %s", json.dumps(hearbeat_data)
                )
                continue

            heart_rate = hearbeat_data["pulse_value"]
            logging.info("Received heart rate %d", heart_rate)
            for player in self.players:
                player.set_bpm(heart_rate)

    def __stop_consumer(self):
        if not self.control_channel.is_closed:
            self.control_channel.cancel()


def main():
    controller = HeartbeatConsumer(control_channel=rmq_channel)
    player = HeartbeatPlayer()
    controller.add_player(player)
    try:
        controller.start()
    except KeyboardInterrupt:
        logging.info("Stopping player")
        controller.stop()


if __name__ == "__main__":
    logging.info("Starting heartbeat player")
    main()
