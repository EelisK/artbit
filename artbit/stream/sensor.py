from typing import Iterator

from artbit.schemas import Heartbeat
from artbit.sensors.grove_fingerclip import GroveFingerclipHeartSensor
from artbit.stream.base import Stream


class SensorStream(Stream[Heartbeat]):
    """
    Iterable class that reads the heartbeat sensor data
    """

    def __init__(self, sensor: GroveFingerclipHeartSensor) -> None:
        self.sensor = sensor

    def __iter__(self) -> Iterator[Heartbeat]:
        self.sensor.open()
        while True:
            self.sensor.update()
            if self.sensor.has_changed:
                message = Heartbeat(
                    timestamp=self.sensor.read_time.isoformat(),
                    pulse_value=self.sensor.sensor_value,
                    is_error=self.sensor.is_error,
                )
                yield message
