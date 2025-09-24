from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer


@dataclass
class FigSetBase:
    file: Annotated[str, typer.Argument(exists=True)]
    matplotlibrc: Annotated[
        Path,
        typer.Option(
            envvar="MXMF_MATPLOTLIBRC_FILE",
            help="matplotlibrc style file",
        ),
    ] = Path("~/.config/mxmftools/matplotlibrc")
    xrange: Annotated[
        tuple[float, float] | None,
        typer.Option(
            "--xrange",
            "-xr",
            help="x index range for figure",
            rich_help_panel="figure set",
        ),
    ] = None
    yrange: Annotated[
        tuple[float, float] | None,
        typer.Option(
            "--yrange",
            "-yr",
            help="y range for figure",
            rich_help_panel="figure set",
        ),
    ] = None
    xlabel: Annotated[
        str | None,
        typer.Option(
            "--xlabel",
            "-xl",
            help="xlabel for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None
    ylabel: Annotated[
        str | None,
        typer.Option(
            "--ylabel",
            "-yl",
            help="ylabel for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    hide_xticks: Annotated[
        bool,
        typer.Option(
            "--hide-xticks/--no-hide-xticks",
            help="whether hide xticks",
            rich_help_panel="figure set",
        ),
    ] = False

    hide_yticks: Annotated[
        bool,
        typer.Option(
            "--hide-yticks/--no-hide-yticks",
            help="whether hide xticks",
            rich_help_panel="figure set",
        ),
    ] = False

    xticks: Annotated[
        str | None,
        typer.Option(
            "--xticks",
            "-xt",
            help="xtick indexes for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    xticklabels: Annotated[
        str | None,
        typer.Option(
            "--xticklabels",
            "-xtl",
            help="xticklabels for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    yticks: Annotated[
        str | None,
        typer.Option(
            "--yticks",
            "-yt",
            help="yticks for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    yticklabels: Annotated[
        str | None,
        typer.Option(
            "--yticklabels",
            "-ytl",
            help="yticklabels for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    title: Annotated[
        str | None,
        typer.Option(
            "--title",
            "-t",
            help="title for Figure.",
            rich_help_panel="figure set",
        ),
    ] = None

    show: Annotated[
        bool,
        typer.Option(
            "--show/--dontshow",
            help="whether show fig",
            rich_help_panel="figure set",
        ),
    ] = True

    save: Annotated[
        str,
        typer.Option(
            "--save",
            help="figure save name or directory",
            rich_help_panel="figure set",
        ),
    ] = "figure.png"

    from_cli: Annotated[
        bool,
        typer.Option(
            "--from_cli",
            # help="figure save name",
            # rich_help_panel="dddd",
            hidden=False,
        ),
    ] = True
