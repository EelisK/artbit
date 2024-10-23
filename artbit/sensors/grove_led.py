import threading
import time
from enum import Enum

import RPi.GPIO as GPIO  # pyright: ignore[reportMissingModuleSource]


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
