import json
from typing import Iterator

from pika.adapters.blocking_connection import BlockingChannel as ControlChannel

from artbit.schemas import Heartbeat
from artbit.stream.base import Stream


class RMQStream(Stream[Heartbeat]):
    """
    Iterable class that reads Heartbeat messages from a RabbitMQ
    """

    def __init__(self, channel: ControlChannel, queue: str) -> None:
        self.channel = channel
        self.queue = queue

    def __iter__(self) -> Iterator[Heartbeat]:
        for method_frame, _, body in self.channel.consume(self.queue):
            self.channel.basic_ack(method_frame.delivery_tag)
            data = json.loads(body)
            heartbeat = Heartbeat(**data)
            yield heartbeat
