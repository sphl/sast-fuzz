import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from cdd import AppConfig
from cdd.container.san import SanitizerOutput
from cdd.grouping import group_by
from cdd.utils.fs import find_files
from cdd.utils.proc import run_program_with_sanitizer, run_with_multiproc

logging.basicConfig(format="%(asctime)s SFA[%(levelname)s]: %(message)s", level=logging.DEBUG, stream=sys.stdout)

# Path of the default config file.
DEFAULT_CONFIG_FILE = Path.cwd() / "config.yml"

app = typer.Typer()


@app.command()
def main(
    shell_cmd: Annotated[
        Optional[str],
        typer.Option(
            "--command",
            help="Shell command to run the sanitizer-instrumented program under test. Note: Use '@@' (w/o the quotes) as placeholder for input files.",
        ),
    ] = None,
    input_dirs: Annotated[
        Optional[List[Path]],
        typer.Option(
            "--input",
            writable=False,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the directory(s) containing the input files for program execution.",
        ),
    ] = None,
    sanitizer_dirs: Annotated[
        Optional[List[Path]],
        typer.Option(
            "--sanitizer-dir",
            writable=False,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to directory(s) with already existing sanitizer output files.",
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output",
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the output directory.",
        ),
    ] = Path.cwd(),
    n_frames: Annotated[
        Optional[int],
        typer.Option(
            "--frames",
            min=1,
            help="Number of stack frames to be included in deduplication. Note: If not specified, all frames are considered.",
        ),
    ] = None,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the YAML configuration file.",
        ),
    ] = DEFAULT_CONFIG_FILE,
):
    app_config = AppConfig.from_yaml(config_file)

    sanitizer_dirs = sanitizer_dirs or []

    if not shell_cmd is None:
        sanitizer_dir = output_dir / "sanitizer"
        sanitizer_dir.mkdir(exist_ok=True)

        run_with_multiproc(
            run_program_with_sanitizer,
            [
                (shell_cmd, input_file, sanitizer_dir)
                for input_file in find_files(input_dirs, blacklist=app_config.inputConfig.blacklist)
            ],
        )

        sanitizer_dirs.append(sanitizer_dir)

    sanitizer_files = find_files(sanitizer_dirs)

    sanitizer_infos = []
    for sanitizer_file in sanitizer_files:
        try:
            sanitizer_infos.append(SanitizerOutput.from_file(sanitizer_file))

        except Exception as ex:
            logging.error(ex)

    summary_file = output_dir / "summary.csv"

    summary = group_by(sanitizer_infos, n_frames)
    summary.to_csv(summary_file)
