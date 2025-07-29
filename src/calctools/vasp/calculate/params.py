from dataclasses import dataclass
from pathlib import Path
from typing import Annotated
import click
import typer

@dataclass
class InputParams:
    input_type: Annotated[
        str,
        typer.Argument(exists=True, click_type=click.Choice(["incar", "kpoints", "potcar", "poscar"])),
        typer.Option(
            "--input-type",
            "-it",
            help="specify input type.",
        ),
    ] = "incar"
    kpt_mesh: Annotated[
        tuple[int, int, int],
        typer.Option(
            "--kpt-mesh",
            "-km",
            help="specify k-point mesh as three integers separated by commas.",
        ),
    ] = (1, 1, 1)
    pesudo: Annotated[
        str | None,
        typer.Option(
            "--pseudo",
            "-p",
            help="specify pseudopotential file or directory.",
        ),
    ] = None

    calcdir: Annotated[Path, typer.Argument(exists=True, file_okay=False)] = Path("calc")
    incar: Annotated[Path, typer.Option("--incar", "-i", exists=True)] = Path("INCAR")
    kpoints: Annotated[Path, typer.Option("--kpoints", "-k", exists=True)] = Path("KPOINTS")
    potcar: Annotated[Path, typer.Option("--potcar", "-p", exists=True)] = Path("POTCAR")
    poscar: Annotated[Path, typer.Option("--poscar", "-o", exists=True)] = Path("POSCAR")
