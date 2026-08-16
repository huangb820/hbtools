from pathlib import Path

import typer

from typing import Annotated


def incar(
    work_dir: Annotated[
        Path, typer.Option("-wd", "--work-dir", help="work directory")
    ] = Path("."),
    file: Annotated[Path, typer.Argument(exists=True)] = Path("INCAR"),
):
    """Print the contents of an INCAR file."""
    print(file.read_text())
