class MACPrefix:
    """
    Represents a MAC address prefix (first 3 bytes of a MAC address).
    """

    def __init__(self, b1: int, b2: int, b3: int):
        for b in [b1, b2, b3]:
            assert 0 <= b <= 255, f"Invalid byte: {b}"
        self.prefix = f"{b1:02x}:{b2:02x}:{b3:02x}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MACPrefix):
            return False

        return self.prefix == other.prefix

    def __str__(self) -> str:
        return self.prefix
