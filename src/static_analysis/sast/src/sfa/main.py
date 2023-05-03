import logging
import sys
from typing import List

import typer
from typing_extensions import Annotated

from sfa.logic.filters.factory import SASTFilter, SASTOutputFilterFactory
from sfa.logic.runner import run_sast_tools
from sfa.logic.tools.factory import SASTTool, SASTToolRunnerFactory
from sfa.utils.io import read

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s SFA[%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = typer.Typer()


@app.command()
def run(
        subject_dir: Annotated[str, typer.Argument(
            writable=True,
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Directory path to the program to be analyzed."
        )],
        output_file: Annotated[str, typer.Argument(
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
) -> int:
    selected_tools = [tool for tool in SASTTool if tool not in excluded_tools]

    factory = SASTToolRunnerFactory(subject_dir)
    runners = list(map(factory.get_runner, selected_tools))

    tool_output = run_sast_tools(runners, parallel)

    print(tool_output)

    return 0


@app.command()
def filter(
        input_file: Annotated[str, typer.Argument(
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=True,
            help="Path to the file containing the SAST tool(s) output."
        )],
        sfi_file: Annotated[str, typer.Argument(
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=True,
            help="Path to the SFI program inspection file."
        )],
        output_file: Annotated[str, typer.Argument(
            writable=True,
            exists=False,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to the output CSV file."
        )],
        output_filters: Annotated[List[SASTFilter], typer.Option("--filter", "-f", help="SAST output filter(s).")] = [
            SASTFilter.REH]
) -> int:
    factory = SASTOutputFilterFactory(sfi_file)
    filters = list(map(factory.get_filter, output_filters))

    tool_output = read(input_file)

    # for f in filters:
    #     tool_output = f.filter(tool_output)

    print(tool_output)

    return 0

# if __name__ == "__main__":
#     app()
