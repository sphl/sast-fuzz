import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from sfa.logic.analyzer import SASTTool, SASTFilter, SASTToolFlags, Analyzer
from sfa.util.proc import get_cpu_count

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
) -> None:
    analyzer = Analyzer(inspec_file)

    flags = analyzer.filter(SASTToolFlags.from_csv(flags_file), filters)

    flags.to_csv(output_file)


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
        Optional[List[SASTTool]], typer.Option("--exclude-tool", help="SAST tool(s) to be excluded from the analysis.")
    ] = None,
    exclude_filters: Annotated[
        Optional[List[SASTFilter]],
        typer.Option("--exclude-filter", help="SAST output filter(s) to be excluded from the analysis."),
    ] = None,
    n_jobs: Annotated[Optional[int], typer.Option("--jobs", "-j", min=1, max=get_cpu_count())] = 1,
) -> None:
    analyzer = Analyzer(inspec_file, subject_dir)

    flags = analyzer.run(SASTTool.all_but(exclude_tools), SASTFilter.all_but(exclude_filters), n_jobs)

    flags.to_csv(output_file)
