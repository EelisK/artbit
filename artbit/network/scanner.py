from dataclasses import dataclass

from scapy.layers.l2 import ARP, Ether
from scapy.packet import Packet
from scapy.sendrecv import srp

from artbit.network.mac import MACPrefix
from artbit.network.vendor import RaspberryPi, Vendor


@dataclass
class Response:
    """
    Represents a device found during a network scan.
    """

    ip: str
    mac: str

    @property
    def mac_prefix(self) -> MACPrefix:
        first, second, third = map(lambda x: int(x, 16), self.mac.split(":")[:3])
        return MACPrefix(first, second, third)


class Scanner:
    """
    Scans a network for devices given an IP address range.
    """

    def __init__(self, address_range: str):
        self.address_range = address_range

    def scan(self) -> list[Response]:
        arp_req_frame: Packet = ARP(pdst=self.address_range)
        broadcast_ether_frame: Packet = Ether(dst="ff:ff:ff:ff:ff:ff")
        broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame  # pyright: ignore[reportUnknownVariableType]
        snd_rcv_list, _ = srp(
            broadcast_ether_arp_req_frame,  # pyright: ignore[reportUnknownArgumentType]
            timeout=1,
            verbose=False,
        )

        result: list[Response] = []
        for i in range(0, len(snd_rcv_list)):
            ip = snd_rcv_list[i][1].psrc
            mac = snd_rcv_list[i][1].hwsrc
            result.append(Response(ip=ip, mac=mac))

        return result


class VendorScanner(Scanner):
    """
    Scans a network for devices from a specific vendor.
    """

    vendor: type[Vendor]

    def __init_subclass__(cls, vendor: type[Vendor]) -> None:
        cls.vendor = vendor

    def scan(self) -> list[Response]:
        return [
            res
            for res in super().scan()
            if res.mac_prefix in self.vendor.mac_prefixes()
        ]


class RaspberryPiScanner(VendorScanner, vendor=RaspberryPi):
    pass
