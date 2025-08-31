from dataclasses import dataclass
from typing import Annotated

import click

from hbtools.utils.common_params import FigSetBase


import typer


@dataclass
class DosParams(FigSetBase):
    file: Annotated[str, typer.Argument(exists=True)] = "vaspout.h5"
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
            min=1,
            max=3,
            help="specific projected mode",
        ),
    ] = 1

    pro_atoms_orbitals: Annotated[
        list[str] | None,
        typer.Option(
            "--pro-atoms-orbitals",
            "-p",
            help="specify projected atoms and orbitals",
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
    ] = "Energy (eV)"
    ylabel: Annotated[
        str | None,
        typer.Option(
            "--ylabel",
            "-yl",
            help="ylabel for Figure.",
            rich_help_panel="figure set",
        ),
    ] = "DOS (states/eV)"
    colors: Annotated[
        str,
        typer.Option(
            "--colors",
            "-c",
            help="title for Figure.",
            rich_help_panel="figure set",
        ),
    ] = "red blue"

    # -----------------------------------------------

    tcolor: Annotated[
        str,
        typer.Option(
            "--tcolor",
            "-tc",
            help="Tdos color for ",
            rich_help_panel="TDOS",
        ),
    ] = "black"

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
    ] = True

    tdos: Annotated[
        bool,
        typer.Option(help="whether plot tdos"),
    ] = True

    tdos_label: Annotated[
        str,
        typer.Option(help="whether plot tdos"),
    ] = "TDOS"
