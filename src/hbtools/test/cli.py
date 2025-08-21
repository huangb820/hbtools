import typer

from ..utils.cli_utils import dataclass_cli
from .params import BandParams

app = typer.Typer(no_args_is_help=True)


@app.command("dddd")
@dataclass_cli
def band(params: BandParams):
    print("hello")
