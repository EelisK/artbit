import time
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
            time.sleep(0.5)
            self.sensor.update()
            if self.sensor.has_changed and self.sensor.sensor_value:
                message = Heartbeat(
                    timestamp=self.sensor.read_time.isoformat(),
                    bpm=self.sensor.sensor_value,
                )
                yield message
