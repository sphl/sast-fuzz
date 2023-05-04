from typing import Dict, Any

from sfa.factory import Factory
from sfa.filter import SASTFilter, SASTOutputFilter
from sfa.filter.reachability import ReachabilityFilter


class FilterFactory(Factory[SASTFilter, SASTOutputFilter]):
    """SAST output filter factory."""

    def _get_creators(self, param: Any) -> Dict[SASTFilter, SASTOutputFilter]:
        return {
            SASTFilter.REH: ReachabilityFilter(param)
        }
