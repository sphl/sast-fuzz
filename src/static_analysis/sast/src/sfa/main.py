import logging
import sys

import typer

from sfa.command import run, filter

logging.basicConfig(
    format="%(asctime)s SFA[%(levelname)s]: %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout
)

app = typer.Typer()

app.add_typer(run.app)
app.add_typer(filter.app)
