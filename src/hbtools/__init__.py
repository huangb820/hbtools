import typer

from .input.cli import app as input_app

# from .subfig import app as subfig_app
from .subfig import subfig
from .vasp.cli import app as plot_app

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)


app.add_typer(plot_app, name="plot")
app.add_typer(input_app, name="input")

app.command()(subfig)


# app.add_typer(subfig_app, name="subfig")
