from dataclasses import dataclass
from typing import Optional


@dataclass
class Heartbeat:
    timestamp: str
    pulse_value: Optional[int]
    is_error: bool
