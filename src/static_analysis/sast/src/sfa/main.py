import logging
import sys
from pathlib import Path
from typing import List

import typer
from typing_extensions import Annotated

from sfa.config import DEFAULT_OUTPUT_FILE
from sfa.logic import has_build_script
from sfa.logic.analyzer import (
    Analyzer,
    GroupingMode,
    SASTFilter,
    SASTTool,
    SASTToolFlags,
)

logging.basicConfig(
    format="%(asctime)s SFA[%(levelname)s]: %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout,
)

app = typer.Typer()


@app.command()
def run(
    subject_dir: Annotated[
        Path,
        typer.Option(
            "--subject",
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the root directory of the program to be analyzed.",
        ),
    ],
    inspec_file: Annotated[
        Path,
        typer.Option(
            "--inspection",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the SFI program inspection file.",
        ),
    ],
    flags_files: Annotated[
        List[Path],
        typer.Option(
            "--flags",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the file(s) containing existing SAST tool flags.",
        ),
    ] = [],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            writable=True,
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the output CSV file.",
        ),
    ] = DEFAULT_OUTPUT_FILE,
    tools: Annotated[List[SASTTool], typer.Option("--tool", help="SAST tool(s) to be used for the analysis.")] = [],
    filters: Annotated[
        List[SASTFilter], typer.Option("--filter", help="SAST flag filter(s) to be applied after the analysis.")
    ] = [],
    grouping: Annotated[GroupingMode, typer.Option("--grouping", help="SAST flag grouping mode.")] = GroupingMode.NONE,
    parallel: Annotated[bool, typer.Option("--parallel", help="Execute SAST tools in parallel.")] = False,
) -> int:
    assert has_build_script(subject_dir), "ERROR: Could not find build (shell-)script!"  # nosec

    analyzer = Analyzer(inspec_file, subject_dir)

    try:
        existing_flags = SASTToolFlags.from_multiple_csvs(flags_files)

        flags = analyzer.run(tools, filters, grouping, parallel, existing_flags)

        flags.to_csv(output_file)

        return 0

    except Exception as ex:
        logging.error(ex)
        return 1
