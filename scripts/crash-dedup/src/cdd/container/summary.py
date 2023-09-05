from collections import namedtuple
from typing import List, Tuple, Optional

from cdd.container.san import SanitizerOutput


DedupEntry = namedtuple("DedupEntry", ["id", "key", "elems"])


class DedupSummary:
    """
    Deduplication summary container.
    """

    def __init__(self, summary: Optional[List[DedupEntry]] = None) -> None:
        self._summary = (summary or [])

    def add(self, id: int, key: Tuple, elems: List[SanitizerOutput]) -> None:
        self._summary.append(DedupEntry(id, key, elems))