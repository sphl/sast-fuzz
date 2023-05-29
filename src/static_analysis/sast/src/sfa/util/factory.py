from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable


class Factory(ABC):
    """
    Abstract factory.
    """

    @abstractmethod
    def _create_instances(self, param: Any) -> Dict:
        pass

    def __init__(self, param: Any) -> None:
        if param is None:
            self._instances = {}
        else:
            self._instances = self._create_instances(param)

    def get_instance(self, key: Any) -> Any:
        return self._instances[key]

    def get_instances(self, keys: Iterable) -> Iterable:
        return map(self.get_instance, keys)
