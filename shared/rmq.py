import os

import pika

_rmq_username = os.getenv("RMQ_USERNAME")
if _rmq_username is None:
    raise ValueError("RMQ_USERNAME environment variable not set")

_rmq_password = os.getenv("RMQ_PASSWORD")
if _rmq_password is None:
    raise ValueError("RMQ_PASSWORD environment variable not set")

_rmq_host = os.getenv("RMQ_HOST")
if _rmq_host is None:
    raise ValueError("RMQ_HOST environment variable not set")

_rmq_port = int(os.getenv("RMQ_PORT", "5672"))
_rmq_vhost = os.getenv("RMQ_VHOST", "/")

_connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=_rmq_host,
        port=_rmq_port,
        virtual_host=_rmq_vhost,
        credentials=pika.PlainCredentials(
            username=_rmq_username,
            password=_rmq_password,
        ),
    )
)
channel = _connection.channel()
