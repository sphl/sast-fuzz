import logging
from itertools import groupby
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from cdd.container.san import SanitizerOutput
from cdd.utils.fs import find_files
from cdd.utils.proc import run_program_with_sanitizer, run_with_multiproc
from cdd.grouping import group_by

app = typer.Typer()


@app.command()
def main(output_dir: Path, shell_cmd: Optional[str] = None, input_dirs: Optional[List[Path]] = None, sanitizer_dirs: Optional[List[Path]] = None, n_frames: Optional[int] = None):
    if not shell_cmd is None:
        run_with_multiproc(run_program_with_sanitizer, [(shell_cmd, input_file, output_dir) for input_file in find_files(input_dirs)])

    san_output_files = find_files(sanitizer_dirs + [output_dir])

    san_outputs = []
    for file in san_output_files:
        try:
            san_outputs.append(SanitizerOutput.from_file(file))

        except Exception as ex:
            logging.error(ex)

    summary = group_by(san_outputs, n_frames)

    print(summary)


if __name__ == "__main__":
    main(Path("/tmp/san_test"), None, None, [Path("/Users/sphl/Projects/sast-fuzz/scripts/crash-dedup/tests/data/crashes")], 1)