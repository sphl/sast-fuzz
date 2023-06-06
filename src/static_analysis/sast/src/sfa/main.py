import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from sfa.config import app_config
from sfa.logic import SASTFlagSet
from sfa.logic.filter import SASTFlagFilterFactory, SASTFlagFilterMode
from sfa.logic.grouping import SASTFlagGroupingFactory, SASTFlagGroupingMode
from sfa.logic.tool_runner import SASTTool, SASTToolRunner, SASTToolRunnerFactory
from sfa.util.proc import run_with_multiproc

logging.basicConfig(format="%(asctime)s SFA[%(levelname)s]: %(message)s", level=logging.DEBUG, stream=sys.stdout)

# Path of the default config file.
DEFAULT_CONFIG_FILE = Path.cwd() / "config.yml"

# Path of the default output file.
DEFAULT_OUTPUT_FILE = Path.cwd() / "output.csv"

app = typer.Typer()


def _starter(runner: SASTToolRunner) -> SASTFlagSet:
    return runner.run()


def run_tools(flags: SASTFlagSet, tools: List[SASTTool], subject_dir: Optional[Path], parallel: bool) -> SASTFlagSet:
    """
    Run SAST tools.

    :param flags:
    :param tools:
    :param subject_dir:
    :param parallel:
    :return:
    """
    if subject_dir is None:
        raise typer.BadParameter("Subject directory is not specified.", param_hint="--subject")

    if not (subject_dir / app_config.BUILD_SCRIPT_NAME).exists():
        raise typer.BadParameter("Build script could not be found in the subject directory.", param_hint="--subject")

    logging.info(f"SAST tools: {', '.join([t.value for t in tools])}")

    n_jobs = 1 if not parallel else len(tools)
    tool_runners = list(SASTToolRunnerFactory(subject_dir).get_instances(tools))

    nested_flags = run_with_multiproc(_starter, tool_runners, n_jobs)

    flags.update(*map(SASTFlagSet, nested_flags))

    return flags


def filter_flags(
    flags: SASTFlagSet, filter_modes: List[SASTFlagFilterMode], inspec_file: Optional[Path]
) -> SASTFlagSet:
    """
    Filter SAST flags.

    :param flags:
    :param filter_modes:
    :param inspec_file:
    :return:
    """
    if inspec_file is None:
        raise typer.BadParameter("SASTFuzz Inspector file is not specified.", param_hint="--inspection")

    for flag_filter in SASTFlagFilterFactory(inspec_file).get_instances(filter_modes):
        flags = flag_filter.filter(flags)

    return flags


def group_flags(flags: SASTFlagSet, grouping_mode: SASTFlagGroupingMode, inspec_file: Optional[Path]) -> SASTFlagSet:
    """
    Group SAST flags.

    :param flags:
    :param grouping_mode:
    :param inspec_file:
    :return:
    """
    if inspec_file is None:
        raise typer.BadParameter("SASTFuzz Inspector file is not specified.", param_hint="--inspection")

    flag_grouping = SASTFlagGroupingFactory(inspec_file).get_instance(grouping_mode)

    return flag_grouping.group(flags)


@app.command(help="Run multiple SAST tools and filter & group their findings.")
def main(
    flag_files: Annotated[
        Optional[List[Path]],
        typer.Option(
            "--flags",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the file(s) containing SAST tool flags.",
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
            help="Path to the root directory of the target program.",
        ),
    ] = None,
    inspec_file: Annotated[
        Optional[Path],
        typer.Option(
            "--inspection",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the SASTFuzz Inspector (SFI) file.",
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
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            writable=True,
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the CSV output file.",
        ),
    ] = DEFAULT_OUTPUT_FILE,
    tools: Annotated[
        Optional[List[SASTTool]],
        typer.Option(
            "--tool",
            help="SAST tool(s) to be used for the analysis. Note: To run the tools, the subject directory must be specified (--subject).",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel", is_flag=True, help="Run the SAST tools in parallel.")] = False,
    filter_modes: Annotated[
        Optional[List[SASTFlagFilterMode]],
        typer.Option(
            "--filter",
            help="Filter(s) to be applied on the SAST flags. Note: To apply the filters, the SFI file must be specified (--inspection).",
        ),
    ] = None,
    grouping_mode: Annotated[
        Optional[SASTFlagGroupingMode],
        typer.Option(
            "--grouping",
            help="Grouping to be applied on the SAST flags. Note: To apply the grouping, the SFI file must be specified (--inspection).",
        ),
    ] = None,
) -> None:
    app_config.load(config_file)

    flags = SASTFlagSet()
    flags.update(*map(SASTFlagSet.from_csv, flag_files or []))

    if tools is not None:
        flags = run_tools(flags, tools, subject_dir, parallel)
    if filter_modes is not None:
        flags = filter_flags(flags, filter_modes, inspec_file)
    if grouping_mode is not None:
        flags = group_flags(flags, grouping_mode, inspec_file)

    flags.to_csv(output_file)