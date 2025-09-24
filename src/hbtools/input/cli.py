import typer
from ..utils.cli_utils import dataclass_cli
from .params import KPOINTSParams,POTCARParams


app = typer.Typer(no_args_is_help=True)


@app.command("init")
@dataclass_cli
def init_config(file_path:str):
    from .init_config import init_config
    init_config()

@app.command("kpoints")
@dataclass_cli
def generate_kpoints(params: KPOINTSParams):
    from .kpoints import write_kpoint_grid,write_kpoints_file

    if params.kpoints_type == "line":
        write_kpoints_file(params)
    else:
        write_kpoint_grid(params)

@app.command("potcar")
@dataclass_cli
def generate_potcar(params: POTCARParams):
    from .potcar import write_potcar as write_potcar_file

    write_potcar_file(params)
