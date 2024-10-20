import logging
import threading
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import RPi.GPIO as GPIO  # type: ignore
import smbus2 as smbus


class GroveLedState(Enum):
    """
    An enumeration to represent the state of the Grove LED
    """

    ON = "on"
    OFF = "off"
    BLINK = "blink"


class GroveLed:
    """
    A class to interact with the Grove LED connected to a Raspberry Pi
    """

    def __init__(self, pin: int) -> None:
        self.__pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.__pin, GPIO.OUT)
        self.__running = True
        self.__state = GroveLedState.OFF
        self.__blink_interval = 0.2
        self.__thread = threading.Thread(name="grove-led", target=self.start)
        self.__thread.start()

    def stop(self):
        self.__running = False
        self.__thread.join()
        GPIO.cleanup()

    def start(self) -> None:
        while self.__running:
            while self.__state == GroveLedState.BLINK:
                self.__toggle_on()
                time.sleep(self.__blink_interval)
                self.__toggle_off()
                time.sleep(self.__blink_interval)
            if self.__state == GroveLedState.ON:
                self.__toggle_on()
            else:
                self.__toggle_off()
            time.sleep(0.5)

    def set_blinking(self):
        self.__state = GroveLedState.BLINK

    def set_off(self):
        self.__state = GroveLedState.OFF

    def set_on(self):
        self.__state = GroveLedState.ON

    def __toggle_on(self) -> None:
        GPIO.output(self.__pin, GPIO.HIGH)

    def __toggle_off(self) -> None:
        GPIO.output(self.__pin, GPIO.LOW)


class GroveFingerclipHeartSensor:
    """
    A class to interact with the Grove Fingerclip Heart Sensor
    connected to a Raspberry Pi
    """

    # The minimum possible BPM value according
    # to the guinness world records
    MIN_POSSIBLE_BPM = 27

    def __init__(self, address: int, led: Optional[GroveLed] = None) -> None:
        self.__prev_sensor_value: Optional[int] = None
        self.__curr_sensor_value: Optional[int] = None
        self.__read_time: Optional[datetime] = None
        self.__bus: Optional[smbus.SMBus] = None
        self.address = address
        self.led = led

    def open(self):
        if GPIO.RPI_REVISION in [2, 3]:
            self.__bus = smbus.SMBus(1)
        else:
            self.__bus = smbus.SMBus(0)

    def close(self):
        if self.__bus is not None:
            self.__bus.close()
        if self.led is not None:
            self.led.stop()

    def update(self) -> None:
        if self.__bus is None:
            raise ValueError("Bus not opened")
        self.__read_time = datetime.now(timezone.utc)
        self.__prev_sensor_value = self.__curr_sensor_value
        try:
            self.__curr_sensor_value = self.__bus.read_byte(self.address)
            if self.led is not None:
                if self.is_error:
                    self.led.set_blinking()
                else:
                    self.led.set_off()
        except IOError:
            logging.error("Error reading from sensor")
            self.__curr_sensor_value = None
            if self.led is not None:
                self.led.set_on()

    @property
    def sensor_value(self) -> Optional[int]:
        return self.__curr_sensor_value

    @property
    def is_error(self) -> bool:
        return (
            self.__curr_sensor_value is None
            or self.__curr_sensor_value <= self.MIN_POSSIBLE_BPM
        )

    @property
    def has_changed(self) -> bool:
        return self.__curr_sensor_value != self.__prev_sensor_value

    @property
    def read_time(self) -> datetime:
        if self.__read_time is None:
            raise ValueError("Sensor value has not been read yet")
        return self.__read_time
