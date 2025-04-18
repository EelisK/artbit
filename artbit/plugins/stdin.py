from typing import Generator

from artbit.plugins.base import Plugin


class StdInPlugin(Plugin):
    """
    A plugin that reads from stdin and sends the data to the output.
    """

    def __init__(self, prompt: str = "Enter BPM: ") -> None:
        self.prompt = prompt

    def values(self) -> Generator[float, None, None]:
        """
        Reads from stdin and yields the values.
        """
        while True:
            line = input(self.prompt)
            if line:
                yield float(line)

    def start(self) -> None:
        """
        Starts the plugin.
        """
        pass

    def stop(self) -> None:
        """
        Stops the plugin.
        """
        pass
