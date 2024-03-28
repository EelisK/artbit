#!/bin/bash

set -eof pipefail

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    echo "Try: sudo $0" 1>&2
    exit 1
fi

case "$1" in
client | server)
    service_type=$1
    read -rp "Enter the RMQ host: " rmq_host
    read -rp "Enter the RMQ port: " rmq_port
    read -rp "Enter the RMQ vhost: " rmq_vhost
    read -rp "Enter the RMQ username: " rmq_username
    ;;
*)
    echo "Usage: $0 [client|server]"
    exit 1
    ;;

esac

service_template=$(
    cat <<EOF
[Unit]
Description=Heartbeat ${service_type} service
Wants=network-online.target
After=network-online.target

[Service]
Environment="RMQ_HOST=${rmq_host}"
Environment="RMQ_PORT=${rmq_port}"
Environment="RMQ_VHOST=${rmq_vhost}"
Environment="RMQ_USERNAME=${rmq_username}"
ExecStart=/usr/bin/python -m $(pwd)/${service_type}
Restart=always
RestartSec=5
User=pi

[Install]
WantedBy=multi-user.target
EOF
)
echo "Creating ${service_type} service with the following configuration:"
echo "$service_template"

echo "$service_template" >"/etc/systemd/system/${service_type}.service"
systemctl enable "${service_type}.service"
systemctl start "${service_type}.service"
