from typing import Optional, TypedDict


class Heartbeat(TypedDict):
    timestamp: str
    pulse_value: Optional[int]
    is_error: bool
