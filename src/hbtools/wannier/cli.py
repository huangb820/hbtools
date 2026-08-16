from pathlib import Path

import typer

from typing import Annotated

app = typer.Typer(no_args_is_help=True)


@app.command("incar")
def incar(
    work_dir: Annotated[
        Path, typer.Option("-wd", "--work-dir", help="work directory")
    ] = Path("."),
    file: Annotated[Path, typer.Argument(exists=True)] = Path("INCAR"),
):
    from .w90.w90_utils import incar as incar_func

    return incar_func(work_dir=work_dir, file=file)