from threading import Lock
from typing import Any


class SingletonMeta(type):
    """
    Thread-safe Singleton, used as a metaclass

    Example:

    class MyClass(metaclass=SingletonMeta):
        pass

    my_instance = MyClass()
    """

    _instances: dict[type, Any] = {}

    _lock: Lock = Lock()

    def __newl__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> "SingletonMeta":
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(name, bases, namespace)
                cls._instances[cls] = instance
        return cls._instances[cls]  # pyright: ignore[reportUnknownVariableType]
