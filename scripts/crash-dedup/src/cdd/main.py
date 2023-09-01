import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def main():
    print("Hello, world!\n")
