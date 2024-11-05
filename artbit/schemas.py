from dataclasses import dataclass


@dataclass
class Heartbeat:
    timestamp: str
    bpm: int
