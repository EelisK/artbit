# artbit 🎨

> etymology: art made with heartbeats

## Setup

To use this project, you need to have a RabbitMQ instance running.
You can configure the connection details using environment variables.

This can be eachieved by creating a `.env` file with the following contents:

```
export RMQ_HOST="your-rmq-instance"
export RMQ_PORT="your-rmq-port"
export RMQ_VHOST="your-rmq-vhost"
export RMQ_USERNAME="your-rmq-username"
export RMQ_PASSWORD="your-rmq-password"
```

## Usage

Development can be done by running the module directly.

```bash
(source .env && python -m artbit)
```
