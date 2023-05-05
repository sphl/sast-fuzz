from itertools import chain
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, Optional, Annotated

import typer

from sfa.tool_runner.base import SASTTool, SASTToolOutput, SASTToolRunner
from sfa.tool_runner.factory import RunnerFactory
from sfa.util.io_sfa import write_flags

app = typer.Typer()


def _starter(runner: SASTToolRunner) -> SASTToolOutput:
    return runner.run()


@app.callback()
def run(
        subject_dir: Annotated[Path, typer.Option(
            "--input",
            "-i",
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the root directory of the program to be analyzed."
        )],
        output_file: Annotated[Path, typer.Option(
            "--output",
            "-o",
            writable=True,
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the output CSV file."
        )],
        excluded_tools: Annotated[Optional[List[SASTTool]], typer.Option(
            "--exclude-tool",
            "-x",
            help="SAST tool(s) to be excluded from the analysis."
        )] = None,
        parallel: Annotated[bool, typer.Option(help="Execute the SAST tools in parallel.")] = True
) -> None:
    selected_tools = [tool for tool in SASTTool if tool not in (excluded_tools or [])]

    factory = RunnerFactory(subject_dir)
    runners = list(map(factory.get_instance, selected_tools))

    if not parallel:
        temp = list(map(_starter, runners))
    else:
        with Pool(cpu_count() - 1) as pool:
            temp = pool.map(_starter, runners)

    flags = set(chain(*temp))

    write_flags(output_file, flags)
