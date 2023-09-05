import logging
import os
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from cdd.container.san import SanitizerOutput
from cdd.grouping import group_by
from cdd.utils.fs import find_files
from cdd.utils.proc import run_program_with_sanitizer, run_with_multiproc

app = typer.Typer()


@app.command()
def main(
    output_dir: Path,
    shell_cmd: Optional[str] = None,
    input_dirs: Optional[List[Path]] = None,
    sanitizer_dirs: Optional[List[Path]] = None,
    n_frames: Optional[int] = None,
):
    sanitizer_dirs = sanitizer_dirs or []

    if not shell_cmd is None:
        sanitizer_dir = output_dir / "sanitizer"
        sanitizer_dir.mkdir(exist_ok=True)

        run_with_multiproc(
            run_program_with_sanitizer,
            [(shell_cmd, input_file, sanitizer_dir) for input_file in find_files(input_dirs)],
        )

        sanitizer_dirs.append(sanitizer_dir)

    sanitizer_files = find_files(sanitizer_dirs)

    sanitizer_infos = []
    for sanitizer_file in sanitizer_files:
        try:
            sanitizer_infos.append(SanitizerOutput.from_file(sanitizer_file))

        except Exception as ex:
            logging.error(ex)

    group_by(sanitizer_infos, n_frames).to_csv(output_dir / "summary.csv")


if __name__ == "__main__":
    main(
        Path("/tmp/san_test"),
        None,
        None,
        [Path("/Users/sphl/Projects/sast-fuzz/scripts/crash-dedup/tests/data/sanitizer")],
        5,
    )
