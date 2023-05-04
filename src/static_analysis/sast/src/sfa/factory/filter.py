from enum import Enum
from typing import Dict, Any

from sfa.factory import Factory

from sfa.filter import SASTFilter
from sfa.filter.reachability import ReachabilityFilter


class FilterFactory(Factory):
    """SAST output filter factory."""

    def _get_creators(self, param: Any) -> Dict[Enum, object]:
        return {
            SASTFilter.REH: ReachabilityFilter(param)
        }