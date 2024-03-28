import json
import logging

from pika.adapters.blocking_connection import BlockingChannel as ControlChannel
from server.player import HeartbeatPlayer
from shared import schemas


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
