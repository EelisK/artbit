import json
import time
import logging

from pika.adapters.blocking_connection import BlockingChannel as ControlChannel
from pika.exceptions import (
    AMQPConnectionError,
    AMQPChannelError,
    ConnectionClosedByBroker,
)


from client.sensor import GroveFingerclipHeartSensor
from shared import schemas


class HeartbeatProducer:
    """
    A class that reads the heartbeat sensor and sends the data
    to a RabbitMQ server
    """

    def __init__(self, sensor: GroveFingerclipHeartSensor, channel: ControlChannel):
        self.sensor = sensor
        self.channel = channel
        self.polling_interval = 0.5

    def start(self):
        self.sensor.open()
        while True:
            try:
                self.sensor.update()
                # To save bandwidth, we only send the message if the
                # pulse value has changed from the previous message
                if self.sensor.has_changed:
                    message: schemas.Heartbeat = {
                        "timestamp": self.sensor.read_time.isoformat(),
                        "pulse_value": self.sensor.sensor_value,
                        "is_error": self.sensor.is_error,
                    }
                    self.channel.basic_publish(
                        "heartbeats",
                        routing_key="heartbeats",
                        body=json.dumps(message),
                    )
                time.sleep(self.polling_interval)
            except (ConnectionClosedByBroker, AMQPChannelError):
                # do not retry, hard fail
                logging.error("Connection to RabbitMQ server closed, exiting")
                break
            except AMQPConnectionError:
                logging.warning("Connection to RabbitMQ server lost, reconnecting")
                continue

    def stop(self):
        self.channel.close()
        self.sensor.close()
