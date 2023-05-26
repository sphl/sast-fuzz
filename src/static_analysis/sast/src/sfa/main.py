import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from sfa.logic import has_build_script
from sfa.logic.analyzer import SASTTool, SASTFilter, GroupingMode, SASTToolFlags, Analyzer

logging.basicConfig(format="%(asctime)s SFA[%(levelname)s]: %(message)s", level=logging.DEBUG, stream=sys.stdout)

app = typer.Typer()


@app.command()
def filter(
    flags_file: Annotated[
        Path,
        typer.Option(
            "--flags-file",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Filepath to the (aggregated) SAST tool flags.",
        ),
    ],
    inspec_file: Annotated[
        Path,
        typer.Option(
            "--inspection-file",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the SFI program inspection file.",
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            writable=True,
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the output CSV file.",
        ),
    ],
    filters: Annotated[
        List[SASTFilter], typer.Option("--filter", "-f", help="SAST output filter(s) to be excluded from the analysis.")
    ],
) -> int:
    analyzer = Analyzer(inspec_file)

    flags = analyzer.filter(SASTToolFlags.from_csv(flags_file), filters)

    flags.to_csv(output_file)

    return 0


@app.command()
def run(
    subject_dir: Annotated[
        Path,
        typer.Option(
            "--subject-root",
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
            "--inspection-file",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the SFI program inspection file.",
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            writable=True,
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the output CSV file.",
        ),
    ],
    exclude_tools: Annotated[
        List[SASTTool], typer.Option("--exclude-tool", help="SAST tool(s) to be excluded from the analysis.")
    ] = [],
    exclude_filters: Annotated[
        List[SASTFilter],
        typer.Option("--exclude-filter", help="SAST output filter(s) to be excluded from the analysis."),
    ] = [],
    grouping: Annotated[GroupingMode, typer.Option("--grouping", help="SAST flag grouping mode.")] = GroupingMode.NONE,
    parallel: Annotated[bool, typer.Option("--parallel", help="Run SAST tools in parallel.")] = False,
) -> int:
    assert has_build_script(subject_dir), "ERROR: Could not find build (shell-)script!"

    analyzer = Analyzer(inspec_file, subject_dir)

    try:
        flags = analyzer.run(SASTTool.all_but(exclude_tools), SASTFilter.all_but(exclude_filters), grouping, parallel)

        flags.to_csv(output_file)

        return 0

    except Exception as ex:
        logging.error(ex)

        return 1
