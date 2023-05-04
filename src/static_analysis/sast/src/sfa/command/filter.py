import logging
from typing import List
from typing_extensions import Annotated

import typer

from sfa.factory.filter import FilterFactory
from sfa.filter import SASTFilter
from sfa.util.io_sfa import read_flags, write_flags

app = typer.Typer()


@app.callback()
def filter(
        input_file: Annotated[str, typer.Option(
            "--input",
            "-i",
            metavar="FLAGS_FILE",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=True,
            help="Path to the file containing the SAST tool(s) flags."
            )],
        sfi_file: Annotated[str, typer.Option(
            "--program-info",
            metavar="SFI_FILE",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=True,
            help="Path to the SFI program inspection file."
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
        flag_filters: Annotated[List[SASTFilter], typer.Option("--filter", "-f", help="SAST output filter(s).")] = [
            SASTFilter.REH]
        ) -> None:
    factory = FilterFactory(sfi_file)
    filters = list(map(factory.get_instance, flag_filters))

    logging.info("Selected filters: %s", str(flag_filters))
    logging.info("Start filtering ...")

    filtered_flags = read_flags(input_file)

    for f in filters:
        filtered_flags = f.filter(filtered_flags)

    write_flags(output_file, filtered_flags)

    logging.info("Done!")
