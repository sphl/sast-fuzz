from enum import Enum

from abc import ABC, abstractmethod
from typing import Any, Dict


class Factory(ABC):
    """Abstract factory."""

    @abstractmethod
    def _get_creators(self, param: Any) -> Dict[Enum, object]:
        pass

    def __init__(self, param: Any) -> None:
        self._creators = self._get_creators(param)

    def get_instance(self, key: Enum) -> object:
        if key not in self._creators.keys():
            raise ValueError("No instance for key found!")

        return self._creators[key]
