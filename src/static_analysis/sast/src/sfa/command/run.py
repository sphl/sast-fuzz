import logging
from itertools import chain
from multiprocessing import Pool, cpu_count
from typing import List, Annotated

import typer

from sfa import SASTToolOutput
from sfa.factory.runner import RunnerFactory
from sfa.tool_runner import SASTTool, SASTToolRunner
from sfa.util.io_sfa import write_flags

app = typer.Typer()


def _starter(runner: SASTToolRunner) -> SASTToolOutput:
    return runner.run()


@app.callback()
def run(
        subject_dir: Annotated[str, typer.Option(
            "--input",
            "-i",
            metavar="SUBJECT_DIR",
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Directory path to the program to be analyzed."
        )],
        output_file: Annotated[str, typer.Option(
            "--output",
            "-o",
            metavar="CSV_FILE",
            writable=True,
            exists=False,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the output CSV file."
        )],
        excluded_tools: Annotated[List[SASTTool], typer.Option(
            "--exclude-tool",
            "-x",
            help="SAST tool(s) to be excluded from the analysis."
        )] = list(),
        parallel: Annotated[bool, typer.Option(help="Execute the SAST tools in parallel.")] = True
) -> None:
    tool_runners = [tool for tool in SASTTool if tool not in excluded_tools]

    factory = RunnerFactory(subject_dir)
    runners = list(map(factory.get_instance, tool_runners))

    logging.info("Selected SAST tools: %s", str(tool_runners))
    logging.info("Start analyzing ...")

    if not parallel:
        temp = list(map(_starter, runners))
    else:
        with Pool(cpu_count() - 1) as pool:
            temp = pool.map(_starter, runners)

    flags = set(chain(*temp))

    write_flags(output_file, flags)

    logging.info("Done!")
