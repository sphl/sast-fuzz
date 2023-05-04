from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, TypeVar, Generic

K = TypeVar("K")
T = TypeVar("T")


class Factory(ABC, Generic[K, T]):
    """Abstract factory."""

    @abstractmethod
    def _get_creators(self, param: Path) -> Dict[K, T]:
        pass

    def __init__(self, param: Path) -> None:
        self._creators = self._get_creators(param)

    def get_instance(self, key: K) -> T:
        if key not in self._creators.keys():
            raise ValueError("No instance for key found!")

        return self._creators[key]
