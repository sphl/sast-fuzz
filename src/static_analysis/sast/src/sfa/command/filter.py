from functools import reduce
from pathlib import Path
from typing import List, Annotated

import typer

from sfa.factory.filter import FilterFactory
from sfa.filter.base import SASTFilter
from sfa.util.io_sfa import read_flags, write_flags

app = typer.Typer()


@app.callback()
def filter(
        input_file: Annotated[Path, typer.Option(
            "--input",
            "-i",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the file containing the SAST tool(s) flags."
            )],
        sfi_file: Annotated[Path, typer.Option(
            "--inspection-file",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the SFI program inspection file."
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
        selected_filters: Annotated[List[SASTFilter], typer.Option("--filter", "-f", help="SAST output filter(s).")] = [
            SASTFilter.REH]
        ) -> None:
    factory = FilterFactory(sfi_file)
    filters = list(map(factory.get_instance, selected_filters))

    filtered_flags = reduce(lambda flags, f: f.filter(flags), filters, read_flags(input_file))

    write_flags(output_file, filtered_flags)
