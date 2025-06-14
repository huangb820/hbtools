from typing import Annotated
import click
import typer
from dataclasses import dataclass


@dataclass
class HeatFigBase:
    colorbar: Annotated[
        bool,
        typer.Option(
            "--colorbar/--no-colorbar",
            "-cb/-ncb",
            help="whether plot clorbar.",
            rich_help_panel="Colormap Figure set",
        ),
    ] = True

    cmap: Annotated[
        str,
        typer.Option(
            "--cmap",
            "-cm",
            help="specific cmap",
            rich_help_panel="Colormap Figure set",
        ),
    ] = "cet_coolwarm"

    cticks: Annotated[
        str | None,
        typer.Option(
            "--cticks",
            "-ct",
            help="colorbar ticks for Figure.",
            rich_help_panel="Colormap Figure set",
        ),
    ] = None

    cticklabels: Annotated[
        str | None,
        typer.Option(
            "--cticklabels",
            "-ctl",
            help="colorbar ticklabels for Figure.",
            rich_help_panel="Colormap Figure set",
        ),
    ] = None
    norm: Annotated[
        str,
        typer.Option(
            "--normalization",
            "-norm",
            help="choose normalization method for colormap ,see  https://matplotlib.org/stable/users/explain/colors/colormapnorms.html",
            click_type=click.Choice(
                [
                    "MyCustom",
                    "Normal",
                    "Logarithmic",
                    "Centered",
                    "SymmetricLogarithmic",
                    "PowerLaw",
                    "TwoSlopeNorm",
                ]
            ),
            rich_help_panel="Colormap Figure set",
        ),
    ] = "MyCustom"

    vrange: Annotated[
        tuple[float, float] | None,
        typer.Option(
            "--vrange",
            "-vr",
            help=" value range for pmode 0",
            rich_help_panel="Colormap Figure set",
        ),
    ] = None

    vcenter: Annotated[
        float,
        typer.Option(
            "--vcenter",
            "-vc",
            help="center ",
            rich_help_panel="Colormap Figure set",
        ),
    ] = 0.0

    power: Annotated[
        float,
        typer.Option(
            "--power",
            help="specific the power of PowerLaw Normalization",
            rich_help_panel="Colormap Figure set",
        ),
    ] = 2.0

    symlogparm: Annotated[
        tuple[float, float],
        typer.Option(
            "--symlogparm",
            help="specific linthresh and linscale for SymmetricLogarithmic Normalization",
            rich_help_panel="Colormap Figure set",
        ),
    ] = (0.1, 0.1)
