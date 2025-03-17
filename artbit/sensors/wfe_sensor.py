import logging
import time
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from gpiozero.spi_devices import MCP3xxx  # pyright: ignore[reportMissingTypeStubs]

logger = logging.getLogger(__name__)


@dataclass
class Voltage:
    """
    Voltage represents a single reading from the VoltageReader
    """

    value: float
    interval: float
    time: float


class VoltageReader:
    """
    A class to read voltages from the WorldFamousElectronics Pulse Sensor

    """

    def __init__(
        self,
        sensor: MCP3xxx,
        read_interval_seconds: float = 0.002,
    ) -> None:
        self.read_interval_seconds = read_interval_seconds
        self.sensor = sensor

    def values(self) -> Generator[Voltage, Any, None]:
        """
        Returns an infinite stream of voltages and the time elapsed between readings
        """
        while True:
            current_time = time.time()
            value = float(self.sensor.value)  # pyright: ignore
            yield Voltage(
                value=value,
                interval=self.read_interval_seconds,
                time=current_time,
            )
            time.sleep(
                max(self.read_interval_seconds - (time.time() - current_time), 0)
            )


class IBIReader:
    """
    A class that reads the interbeat interval based on voltage
    """

    def __init__(
        self,
        voltage_reader: VoltageReader,
        threshold: float = 0.60,
    ) -> None:
        self.voltage_reader = voltage_reader
        self.threshold = threshold
        self.peak_voltage = 0.5
        self.low_voltage = 0.5
        self.interbeat_interval = 0.6  # Initial ibi 600ms (100 BPM)
        self.last_pulse_sample_counter = 0.0
        self.first_pulse = True
        self.second_pulse = False
        self.sample_counter = 0
        self.pulse = False
        self.rates = [0.0] * 10

    def values(self) -> Generator[float, Any, None]:
        """
        Returns an infinite stream of interbeat intervals in seconds
        """
        generator = self.voltage_reader.values()
        for signal in generator:
            self.sample_counter += signal.interval
            num_samples = self.sample_counter - self.last_pulse_sample_counter
            # dicrotic pulse is an abnormal carotid pulse found in conjunction
            # with certain conditions characterised by low cardiac output
            non_dicrotic_pulse = num_samples > (self.interbeat_interval / 5) * 3

            if signal.value < self.threshold and non_dicrotic_pulse:
                if signal.value < self.low_voltage:
                    self.low_voltage = signal.value

            if signal.value > self.threshold and signal.value > self.peak_voltage:
                self.peak_voltage = signal.value

            is_new_pulse = (
                num_samples > 0.25
                and signal.value > self.threshold
                and not self.pulse
                and non_dicrotic_pulse
            )
            if is_new_pulse:
                self.pulse = True
                self.interbeat_interval = (
                    self.sample_counter - self.last_pulse_sample_counter
                )
                self.last_pulse_sample_counter = self.sample_counter

                # Second iteration with a valid beat,
                # simulate the rates for the first 10 IBIs
                if self.second_pulse:
                    self.second_pulse = False
                    for i in range(10):
                        self.rates[i] = self.interbeat_interval

                # First iteration with a valid pulse
                # skip this to calculate the average interbeat interval
                # starting from the second beat
                if self.first_pulse:
                    self.first_pulse = False
                    self.second_pulse = True
                    continue

                average_interbeat_interval = sum(self.rates[:-1])
                self.rates = self.rates[1:] + [self.interbeat_interval]
                average_interbeat_interval += self.interbeat_interval
                average_interbeat_interval /= len(self.rates)
                yield average_interbeat_interval

            is_new_nopulse = signal.value < self.threshold and self.pulse
            if is_new_nopulse:
                self.pulse = False
                self.low_voltage = self.peak_voltage = self.threshold

            if num_samples > 2.5:
                logger.warning(
                    "Voltage reader interval is too high, resetting state",
                    extra={"interval": num_samples},
                )
                self.__reset_state()

    def __reset_state(self):
        self.peak_voltage = self.low_voltage = 0.5
        self.rates = [0.0] * 10
        self.last_pulse_sample_counter = self.sample_counter

        self.second_pulse = False
        self.first_pulse = True
        self.pulse = False

        self.interbeat_interval = 0.6
