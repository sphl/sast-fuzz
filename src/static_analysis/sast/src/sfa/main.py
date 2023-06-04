import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from sfa.config import config
from sfa.logic import SASTToolFlags
from sfa.logic.filter import FilterFactory, SASTFilter
from sfa.logic.grouping import GroupingFactory, GroupingMode
from sfa.logic.tool_runner import RunnerFactory, SASTTool, SASTToolRunner
from sfa.util.proc import run_with_multiproc

logging.basicConfig(format="%(asctime)s SFA[%(levelname)s]: %(message)s", level=logging.DEBUG, stream=sys.stdout)

app = typer.Typer()


def _starter(runner: SASTToolRunner) -> SASTToolFlags:
    return runner.run()


def run_tools(
    flags: SASTToolFlags, subject_dir: Optional[Path], tools: Optional[List[SASTTool]], parallel: bool
) -> SASTToolFlags:
    """
    Run SAST tools.

    :param flags:
    :param subject_dir:
    :param tools:
    :param parallel:
    :return:
    """
    if tools is None:
        return flags

    if subject_dir is None:
        raise Exception("ERROR: Subject directory is not specified!")

    if not (subject_dir / "build.sh").exists():
        raise Exception("ERROR: 'build.sh' not found in the subject directory!")

    logging.info(f"SAST tools: {', '.join([t.value for t in tools])}")

    n_jobs = 1 if not parallel else len(tools)

    runner_insts = list(RunnerFactory(subject_dir).get_instances(tools))

    nested_flags = run_with_multiproc(_starter, runner_insts, n_jobs)
    flags.update(*map(SASTToolFlags, nested_flags))

    return flags


def run_filters(flags: SASTToolFlags, inspec_file: Path, filters: Optional[List[SASTFilter]]) -> SASTToolFlags:
    """
    Run SAST flag filters.

    :param flags:
    :param inspec_file:
    :param filters:
    :return:
    """
    if filters is not None:
        for filter_inst in FilterFactory(inspec_file).get_instances(filters):
            flags = filter_inst.filter(flags)

    return flags


def run_grouping(flags: SASTToolFlags, inspec_file: Path, grouping: Optional[GroupingMode]) -> SASTToolFlags:
    """
    Run SAST flag grouping.

    :param flags:
    :param inspec_file:
    :param grouping:
    :return:
    """
    if grouping is not None:
        grouping_inst = GroupingFactory(inspec_file).get_instance(grouping)

        flags = grouping_inst.group(flags)

    return flags


@app.command()
def run(
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
        Optional[List[Path]],
        typer.Option(
            "--flags",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the file(s) containing existing SAST tool flags.",
        ),
    ] = None,
    subject_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--subject",
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the root directory of the program to be analyzed.",
        ),
    ] = None,
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
    ] = (Path.cwd() / "output.csv"),
    tools: Annotated[
        Optional[List[SASTTool]], typer.Option("--tool", help="SAST tool(s) to be used for the analysis.")
    ] = None,
    filters: Annotated[
        Optional[List[SASTFilter]],
        typer.Option("--filter", help="SAST flag filter(s) to be applied after the analysis."),
    ] = None,
    grouping: Annotated[Optional[GroupingMode], typer.Option("--grouping", help="SAST flag grouping mode.")] = None,
    parallel: Annotated[bool, typer.Option("--parallel", help="Execute SAST tools in parallel.")] = False,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the configuration YAML file.",
        ),
    ] = (Path.cwd() / "config.yml"),
) -> None:
    """
    Run SAST tools and filter & group their findings.
    """
    try:
        config.load_from_file(config_file)

        flags = SASTToolFlags()
        flags.update(*map(SASTToolFlags.from_csv, flags_files or []))

        flags = run_tools(flags, subject_dir, tools, parallel)
        flags = run_filters(flags, inspec_file, filters)
        flags = run_grouping(flags, inspec_file, grouping)

        flags.to_csv(output_file)

    except Exception as ex:
        logging.error(ex)
