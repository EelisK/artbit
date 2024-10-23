from abc import ABC, abstractmethod

from artbit.network.mac import MACPrefix


class Vendor(ABC):
    """
    Represents a device manufacturer.
    """

    @staticmethod
    @abstractmethod
    def mac_prefixes() -> list[MACPrefix]:
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass


class RaspberryPi(Vendor):
    @staticmethod
    def mac_prefixes() -> list[MACPrefix]:
        return [
            MACPrefix(0x28, 0xCD, 0xC1),
            MACPrefix(0xB8, 0x27, 0xEB),
            MACPrefix(0xD8, 0x3A, 0xDD),
            MACPrefix(0xDC, 0xA6, 0x32),
            MACPrefix(0xE4, 0x5F, 0x01),
        ]

    @staticmethod
    def name() -> str:
        return "Raspberry Pi"
