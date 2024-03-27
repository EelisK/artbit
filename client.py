import json
import time
import logging
from typing import Optional

from pika.adapters.blocking_connection import BlockingChannel as ControlChannel
from pika.exceptions import (
    AMQPConnectionError,
    AMQPChannelError,
    ConnectionClosedByBroker,
)
import smbus2 as smbus
import RPi.GPIO as GPIO

from datetime import datetime, timezone

from shared import schemas
from shared.rmq import channel as rmq_channel


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


class GroveFingerclipHeartSensor:
    """
    A class to interact with the Grove Fingerclip Heart Sensor
    connected to a Raspberry Pi
    """

    address = 0x50

    def __init__(self) -> None:
        self.__prev_sensor_value: Optional[int] = None
        self.__curr_sensor_value: Optional[int] = None
        self.__read_time: Optional[datetime] = None
        self.__bus: Optional[smbus.SMBus] = None

    def open(self):
        if GPIO.RPI_REVISION in [2, 3]:
            self.__bus = smbus.SMBus(1)
        else:
            self.__bus = smbus.SMBus(0)

    def close(self):
        if self.__bus is not None:
            self.__bus.close()

    def update(self) -> None:
        if self.__bus is None:
            raise ValueError("Bus not opened")
        self.__read_time = datetime.now(timezone.utc)
        try:
            self.__curr_sensor_value = self.__bus.read_byte(self.address)
        except IOError:
            logging.error("Error reading from sensor")
            self.__curr_sensor_value = None

    @property
    def sensor_value(self) -> Optional[int]:
        return self.__curr_sensor_value

    @property
    def is_error(self) -> bool:
        return self.__curr_sensor_value is None or self.__curr_sensor_value == 0

    @property
    def has_changed(self) -> bool:
        return self.__curr_sensor_value != self.__prev_sensor_value

    @property
    def read_time(self) -> datetime:
        if self.__read_time is None:
            raise ValueError("Sensor value has not been read yet")
        return self.__read_time


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


def main():
    sensor = GroveFingerclipHeartSensor()
    producer = HeartbeatProducer(sensor, rmq_channel)
    try:
        producer.start()
    except KeyboardInterrupt:
        logging.info("Exiting...")
    finally:
        producer.stop()


if __name__ == "__main__":
    logging.info("Starting heartbeat producer")
    main()
