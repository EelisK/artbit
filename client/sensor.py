import logging
from typing import Optional
import smbus2 as smbus
import RPi.GPIO as GPIO

from datetime import datetime, timezone


class GroveLed:
    """
    A class to interact with the Grove LED connected to a Raspberry Pi
    """

    def __init__(self, pin: int) -> None:
        self.__pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.__pin, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()

    def turn_on(self) -> None:
        GPIO.output(self.__pin, GPIO.HIGH)

    def turn_off(self) -> None:
        GPIO.output(self.__pin, GPIO.LOW)


class GroveFingerclipHeartSensor:
    """
    A class to interact with the Grove Fingerclip Heart Sensor
    connected to a Raspberry Pi
    """

    def __init__(self, address: int, error_pin: Optional[int] = None) -> None:
        self.__prev_sensor_value: Optional[int] = None
        self.__curr_sensor_value: Optional[int] = None
        self.__read_time: Optional[datetime] = None
        self.__bus: Optional[smbus.SMBus] = None
        self.address = address
        self.error_sensor = None
        if error_pin is not None:
            self.error_sensor = GroveLed(pin=error_pin)

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
        if self.error_sensor is not None:
            if self.is_error:
                self.error_sensor.turn_on()
            else:
                self.error_sensor.turn_off()

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
