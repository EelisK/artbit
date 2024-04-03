import logging
from client.producer import HeartbeatProducer
from client.sensor import GroveFingerclipHeartSensor
from shared.rmq import channel as rmq_channel


logging.basicConfig(
    level=logging.INFO,
    format="(%(threadName)-9s) %(message)s",
)


def main():
    sensor = GroveFingerclipHeartSensor(address=0x50, error_pin=6)
    producer = HeartbeatProducer(sensor, rmq_channel)
    try:
        producer.start()
    except KeyboardInterrupt:
        logging.info("Exiting...")
    finally:
        producer.stop()


if __name__ == "__main__":
    logging.info("Starting heartbeat producer")
    main()
