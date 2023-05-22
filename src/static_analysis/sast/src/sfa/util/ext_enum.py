from enum import Enum
from typing import List


class ExtendedEnum(Enum):
    """
    Enum extension with more functionality.
    """

    @classmethod
    def values(cls) -> List:
        return [e for e in cls]

    @classmethod
    def all_but(cls, excluded: List) -> List:
        return [e for e in cls if e not in excluded]
