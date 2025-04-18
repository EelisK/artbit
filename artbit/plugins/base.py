from abc import ABC, abstractmethod
from typing import Generator


class Plugin(ABC):
    """
    Plugin is a class used to determine how artbit should receive data
    """

    @abstractmethod
    def values(self) -> Generator[float, None, None]:
        """
        Returns a generator that yields values
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Starts the plugin
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the plugin
        """
        pass
