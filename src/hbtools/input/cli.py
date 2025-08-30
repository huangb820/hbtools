from pathlib import Path
import pprint
from typing import Annotated
import click
import typer
from ..utils.cli_utils import dataclass_cli
from .params import InputParams,POTCARParams


app = typer.Typer(no_args_is_help=True)


@app.command("init")
def init_config(params:POTCARParams):
    from .potcar import init_config
    init_config()

@app.command("kpoints")
@dataclass_cli
def generate_kpoints(params: InputParams):
    from .kpoints import write_kpoint_grid,write_kpoints_file
    if params.output_filename is None:
        params.output_filename = "KPOINTS"

    if params.kpoints_type == "line":
        write_kpoints_file(params)
    else:
        write_kpoint_grid(params)

@app.command("potcar")
@dataclass_cli
def generate_potcar(params: POTCARParams):
    from .potcar import write_potcar as write_potcar_file
    if params.output_filename is None:
        params.output_filename = "POTCAR"

    write_potcar_file(params)
