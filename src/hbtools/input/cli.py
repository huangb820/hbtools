from pathlib import Path
import pprint
from typing import Annotated
import click
import typer
from ..utils.cli_utils import dataclass_cli
from .params import InputParams
from .kpoints import *

app = typer.Typer(no_args_is_help=True)


@app.command("kpoints")
@dataclass_cli
def generate_kpoints(params: InputParams):
    if params.output_filename is None:
        params.output_filename = "KPOINTS"

    if params.kpoints_type == "line":
        write_kpoints_file(params)
    else:
        write_kpoint_grid(params)
