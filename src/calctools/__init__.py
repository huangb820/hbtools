import typer
from .vasp.cli import app as vasp_app

# from .subfig import app as subfig_app
from .subfig import subfig

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)

app.add_typer(vasp_app, name="vasp")
app.command()(subfig)


# app.add_typer(subfig_app, name="subfig")
