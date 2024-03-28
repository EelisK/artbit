import logging

from server.consumer import HeartbeatConsumer
from server.player import HeartbeatPlayer
from shared.rmq import channel as rmq_channel

logging.basicConfig(
    level=logging.INFO,
    format="(%(threadName)-9s) %(message)s",
)


def main():
    controller = HeartbeatConsumer(control_channel=rmq_channel)
    player = HeartbeatPlayer()
    controller.add_player(player)
    try:
        controller.start()
    except KeyboardInterrupt:
        logging.info("Stopping player")
        controller.stop()


if __name__ == "__main__":
    logging.info("Starting heartbeat player")
    main()
