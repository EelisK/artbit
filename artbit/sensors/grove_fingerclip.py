import logging
from datetime import datetime, timezone
from typing import Optional

import RPi.GPIO as GPIO  # pyright: ignore[reportMissingModuleSource]
import smbus2 as smbus


class GroveFingerclipHeartSensor:
    """
    A class to interact with the Grove Fingerclip Heart Sensor
    connected to a Raspberry Pi
    """

    def __init__(self, address: int) -> None:
        self.__prev_sensor_value: Optional[int] = None
        self.__curr_sensor_value: Optional[int] = None
        self.__read_time: Optional[datetime] = None
        self.__bus: Optional[smbus.SMBus] = None
        self.address = address

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
        self.__prev_sensor_value = self.__curr_sensor_value
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
        return self.__curr_sensor_value is None

    @property
    def has_changed(self) -> bool:
        return self.__curr_sensor_value != self.__prev_sensor_value

    @property
    def read_time(self) -> datetime:
        if self.__read_time is None:
            raise ValueError("Sensor value has not been read yet")
        return self.__read_time
