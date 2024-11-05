from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class Stream(ABC, Iterable[T], Generic[T]):
    """
    Abstract class for iterable streams

    """

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...
