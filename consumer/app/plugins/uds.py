import logging
import os
import socket
from typing import Generator

from app.plugins.base import Plugin


class UDSPlugin(Plugin):
    """
    A plugin that reads from a UDS socket
    """

    def __init__(self, path: str, timeout: float = 0.1) -> None:
        self.path = path
        self.timeout = timeout
        self.server = None
        self.connection = None

    def start(self) -> None:
        """
        Starts the plugin.
        """

        # remove the socket file if it already exists
        try:
            os.unlink(self.path)
        except OSError:
            if os.path.exists(self.path):
                raise

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.path)
        self.server.listen(1)

    def stop(self) -> None:
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            if self.server:
                self.server.close()
                self.server = None
        finally:
            os.unlink(self.path)

    def values(self) -> Generator[float, None, None]:
        """
        Reads from the UDS socket and yields the values.
        """
        if self.server is None:
            raise RuntimeError(
                "Plugin not started. Call start() before using values()."
            )

        self.connection, _ = self.server.accept()
        logging.info(f"Client connected to {self.path}")

        while True:
            try:
                data = self.connection.recv(1024)
                if not data:
                    logging.info("Client disconnected, closing connection")
                    self.connection.close()
                    logging.info("Waiting for new client")
                    self.connection, _ = self.server.accept()
                    logging.info(f"Client connected to {self.path}")
                    continue
                for line in data.decode("utf-8").splitlines():
                    if line:
                        yield float(line)
            except (BlockingIOError, TimeoutError):
                pass
            except Exception:
                logging.exception("Error reading from UDS socket")
                raise
