import sys

import typer

from . import vasp

from .subfig import subfig
from .vasp.cli import app as plot_app
from .input.cli import app as input_app
from .calc.cli import app as calc_app
sys.modules["hbtools.plot"] = vasp

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)


app.add_typer(plot_app, name="plot")
app.add_typer(input_app, name="input")
app.add_typer(calc_app, name="calc")

app.command()(subfig)
