from enum import Enum
from typing import List, Union

from sfa.logic.filters.base import SASTOutputFilter
from sfa.logic.filters.reachability import ReachabilityFilter


class SASTFilter(Enum):
    REH = "reachability"

    @classmethod
    def values(cls) -> List[str]:
        return [_filter.value for _filter in cls]


class SASTOutputFilterFactory:
    """Factory for creating SAST output filters."""

    def __init__(self, sfi_file: str) -> None:
        self._creators = {
            SASTFilter.REH: ReachabilityFilter(sfi_file)
        }

    def get_filter(self, _filter: Union[str, SASTFilter]) -> SASTOutputFilter:
        """Get a specific SAST output filter.

        :param _filter: SAST filter
        :return: Output filter
        """
        if type(_filter) is str:
            key = SASTFilter(_filter)
        elif type(_filter) is SASTFilter:
            key = _filter
        else:
            raise ValueError("Wrong argument type!")

        return self._creators[key]
