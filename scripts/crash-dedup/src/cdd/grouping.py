from itertools import groupby
from typing import List, Optional

from cdd.container.san import SanitizerOutput
from cdd.container.summary import DedupEntry, DedupSummary


def group_by(san_outputs: List[SanitizerOutput], n_frames: Optional[int] = None) -> DedupSummary:
    """
    Group/deduplicate sanitizer outputs.

    :param san_outputs:
    :param n_frames:
    :return:
    """
    keyfunc = lambda s: s.sorting_key(n_frames)

    return DedupSummary([DedupEntry(i, k, list(g)) for i, (k, g) in enumerate(groupby(sorted(san_outputs, key=keyfunc), key=keyfunc))])