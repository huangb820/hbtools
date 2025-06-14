from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import click

from hbtools.utils.common_params import FigSetBase, HeatFigBase


import typer


@dataclass
class BandParams(HeatFigBase, FigSetBase):
    file: Annotated[Path, typer.Argument(exists=True)] = Path("vaspout.h5")
    vaspfileformat: Annotated[
        str,
        typer.Option(
            "-vf",
            "--vaspfileformat",
            click_type=click.Choice(["h5", "xml"]),
            envvar="MXMF_VASPFILE_FORMAT",
            help="read file format.",
        ),
    ] = "h5"
    efermi: Annotated[
        float | None,
        typer.Option("-ef", "--efermi", help="specify fermi energy."),
    ] = None
    spin: Annotated[
        int | None, typer.Option("-s", "--spin", help="specify which spin to plot")
    ] = None
    pmode: Annotated[
        int,
        typer.Option(
            "--pmode",
            "-pm",
            min=0,
            max=1,
            help="specific projected mode",
        ),
    ] = 0
    pro_atoms_orbitals: Annotated[
        list[str] | None,
        typer.Option(
            "--pro-atoms-orbitals",
            "-p",
            help="specify projected atoms and orbitals",
        ),
    ] = None

    fix_order: Annotated[
        bool,
        typer.Option(help="reorder band for vasp give the wrong order when ncore > 1"),
    ] = False

    xrange: Annotated[
        tuple[float, float] | None,
        typer.Option(
            "--xrange",
            "-xr",
            help="x index range for figure",
            click_type=click.INT,
            rich_help_panel="figure set",
        ),
    ] = (0, -1)
    yrange: Annotated[
        tuple[float, float] | None,
        typer.Option(
            "--yrange",
            "-yr",
            help="y range for figure",
            rich_help_panel="figure set",
        ),
    ] = (-4, 6)
    ylabel: Annotated[
        str | None,
        typer.Option(
            "--ylabel",
            "-yl",
            help="ylabel for Figure.",
            rich_help_panel="figure set",
        ),
    ] = "Energy (eV)"
    hide_xticks: Annotated[
        bool,
        typer.Option(
            "--hide-xticks/--no-hide-xticks",
            help="whether hide xticks",
            rich_help_panel="figure set",
        ),
    ] = True
    colors: Annotated[
        str,
        typer.Option(
            "--colors",
            "-c",
            help="colors for Figure.",
            rich_help_panel="figure set",
        ),
    ] = "red blue"

    # -----------------------------------------------

    scale: Annotated[
        float,
        typer.Option(
            "--scale",
            help="specific scatter scale for pmode 1",
            rich_help_panel="pmode 1 set",
        ),
    ] = 5

    hollow: Annotated[
        bool,
        typer.Option(
            "--hollow",
            help="whether hollow points for scatter plot",
            rich_help_panel="pmode 1 set",
        ),
    ] = False

    labels: Annotated[
        str | None,
        typer.Option(
            "--labels",
            help="specific legend labels for lines, split by ';'",
        ),
    ] = None

    legend: Annotated[
        bool,
        typer.Option(
            "--legend/--nolegend",
            help="whether show legend",
        ),
    ] = False
