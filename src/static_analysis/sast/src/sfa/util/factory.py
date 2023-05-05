from abc import ABC, abstractmethod
from typing import Dict, TypeVar, Generic

D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")


class Factory(ABC, Generic[D, E, F]):
    """Abstract factory."""

    @abstractmethod
    def _get_creators(self, param: D) -> Dict[E, F]:
        pass

    def __init__(self, param: D) -> None:
        self._creators = self._get_creators(param)

    def get_instance(self, key: E) -> F:
        if key not in self._creators.keys():
            raise ValueError("No instance for key found!")

        return self._creators[key]
