#!/usr/bin/env python
import json
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

from scapy import interfaces
from scapy.layers.l2 import ARP, Ether
from scapy.packet import Packet
from scapy.sendrecv import srp

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="(%(threadName)-9s) %(message)s",
)


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


@dataclass
class ScanResult:
    """
    Represents a device found during a network scan.
    """

    ip: str
    mac: str

    @property
    def mac_prefix(self) -> MACPrefix:
        first, second, third = map(lambda x: int(x, 16), self.mac.split(":")[:3])
        return MACPrefix(first, second, third)


class DeviceScanner:
    """
    Scans a network for devices given an IP address range.
    """

    def __init__(self, address_range: str):
        self.address_range = address_range

    def scan(self) -> list[ScanResult]:
        arp_req_frame: Packet = ARP(pdst=self.address_range)
        broadcast_ether_frame: Packet = Ether(dst="ff:ff:ff:ff:ff:ff")
        broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame  # type: ignore
        snd_rcv_list, _ = srp(
            broadcast_ether_arp_req_frame,  # type: ignore
            timeout=1,
            verbose=False,
        )

        result: list[ScanResult] = []
        for i in range(0, len(snd_rcv_list)):
            ip = snd_rcv_list[i][1].psrc
            mac = snd_rcv_list[i][1].hwsrc
            result.append(ScanResult(ip=ip, mac=mac))

        return result


class VendorDeviceScanner(DeviceScanner):
    """
    Scans a network for devices from a specific vendor.
    """

    def __init__(self, address_range: str, vendors: list[type[Vendor]]):
        super().__init__(address_range)
        self.vendors = vendors

    def scan(self) -> list[ScanResult]:
        return [
            res
            for res in super().scan()
            if any(res.mac_prefix in vendor.mac_prefixes() for vendor in self.vendors)
        ]


if __name__ == "__main__":
    iface = interfaces.get_working_if()
    if iface is None:
        logging.critical("No working interface found")
        exit(1)

    if iface.ip is None:
        logging.critical("No IP address found")
        exit(1)

    ip_range = ".".join(iface.ip.split(".")[0:3]) + ".0/24"
    pi_scanner = VendorDeviceScanner(ip_range, [RaspberryPi])
    scan_result = pi_scanner.scan()

    output = {
        "_meta": {},
        "raspberrypi": {
            "hosts": [result.ip for result in scan_result],
        },
    }
    print(json.dumps(output))
