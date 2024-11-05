import argparse
import dataclasses
import json
import logging
import os

from artbit.schemas import Heartbeat
from artbit.sensors.grove_fingerclip import GroveFingerclipHeartSensor
from artbit.stream.base import Stream
from artbit.stream.sensor import SensorStream

logging.basicConfig(
    level=logging.INFO,
    format="(%(threadName)-9s) %(message)s",
)


if __name__ != "__main__":
    raise RuntimeError("This module should be run as a script")

parser = argparse.ArgumentParser()
# Add sensor argument group
sensor_args = parser.add_argument_group("Sensor")
sensor_args.add_argument(
    "--sensor-address",
    type=int,
    help="Grove Fingerclip sensor address",
    default=int(os.getenv("SENSOR_ADDRESS", "80")),  # 0x50
)
# Parse the arguments
args = parser.parse_args()


# Create the stream
sensor = GroveFingerclipHeartSensor(args.sensor_address)
stream: Stream[Heartbeat] = SensorStream(sensor)
heartbeats: list[Heartbeat] = []

try:
    for beat in stream:
        logging.info(f"Received heartbeat: {beat}")
        heartbeats.append(beat)
except (KeyboardInterrupt, OSError):
    logging.info("Stopping the application")
finally:
    with open("heartbeat.json", "w") as f:
        f.write(json.dumps([dataclasses.asdict(x) for x in heartbeats]))
