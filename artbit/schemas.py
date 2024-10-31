from dataclasses import dataclass


@dataclass
class Heartbeat:
    # TODO: add sender
    timestamp: str
    bpm: int
