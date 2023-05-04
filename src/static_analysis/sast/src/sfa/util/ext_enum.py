from enum import Enum
from typing import List


class ExtendedEnum(Enum):

    @classmethod
    def values(cls) -> List[str]:
        return [item.value for item in cls]
