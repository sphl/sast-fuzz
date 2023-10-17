# Copyright 2023 Stephan Lipp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def __init__(
        self, n_frames: Optional[int], consider_lines: bool, summary: Optional[List[DedupEntry]] = None
    ) -> None:
        self.n_frames = n_frames
        self.consider_lines = consider_lines
        self.summary = summary or []

    def add(self, id: int, key: Tuple, elems: List[SanitizerOutput]) -> None:
        self.summary.append(DedupEntry(id, key, elems))

    def to_csv(self, file: Path) -> None:
        with file.open("w+") as csv_file:
            csv_file.write(
                "bug_id,n_dedup_frames,consider_lines,input_name,sanitizer,vuln_type,stack_trace,n_frames" + os.linesep
            )

            for entry in self.summary:
                for san_output in entry.elems:
                    frame_str = str(self.n_frames) if self.n_frames else "-"
                    stack_trace = "-".join(
                        [f"#{frame.id}:{frame.file}:{frame.function}:{frame.line}" for frame in san_output.stack_trace]
                    )
                    line = CSV_SEP.join(
                        (
                            str(entry.bug_id),
                            frame_str,
                            str(self.consider_lines),
                            str(san_output.input_id).replace(CSV_SEP, "-"),
                            san_output.san,
                            san_output.vtype,
                            stack_trace,
                            str(len(san_output.stack_trace)),
                        )
                    )

                    csv_file.write(line + os.linesep)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DedupSummary):
            return False

        return self.n_frames == o.n_frames and self.summary == o.summary
