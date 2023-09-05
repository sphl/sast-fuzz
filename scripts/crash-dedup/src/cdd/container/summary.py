import os
from collections import namedtuple
from pathlib import Path
from typing import List, Optional, Tuple

from cdd.container.san import SanitizerOutput

# CSV separator
CSV_SEP: str = ","


DedupEntry = namedtuple("DedupEntry", ["bug_id", "key", "elems"])


class DedupSummary:
    """
    Deduplication summary container.
    """

    def __init__(self, n_frames: Optional[int], summary: Optional[List[DedupEntry]] = None) -> None:
        self.n_frames = n_frames
        self.summary = summary or []

    def add(self, id: int, key: Tuple, elems: List[SanitizerOutput]) -> None:
        self.summary.append(DedupEntry(id, key, elems))

    def to_csv(self, file: Path) -> None:
        with file.open("w+") as csv_file:
            csv_file.write("bug_id,n_frames,input_name,vuln_type,stack_trace" + os.linesep)

            for entry in self.summary:
                for san_output in entry.elems:
                    frame_str = str(self.n_frames) if self.n_frames else "-"
                    stack_trace = "-".join(
                        [f"#{frame.id}:{frame.file}:{frame.function}:{frame.line}" for frame in san_output.stack_trace]
                    )
                    line = CSV_SEP.join(
                        (str(entry.bug_id), frame_str, str(san_output.input_id), san_output.vtype, stack_trace)
                    )

                    csv_file.write(line + os.linesep)
