from dataclasses import dataclass


@dataclass
class Voltage:
    value: float
    time: float
    interval: float


@dataclass
class Heartbeat:
    timestamp: str
    bpm: int
