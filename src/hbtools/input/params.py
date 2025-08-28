from pathlib import Path
import click
import typer

from dataclasses import dataclass, field
from typing import Annotated


@dataclass
class InputParams:
    # 写死的高对称点（可扩展）
    # 默认参数
    work_dir: Annotated[
        Path, typer.Option("-wd", "--work-dir", help="work directory")
    ] = Path(".")
    input_filename: Annotated[
        str, typer.Option("-if", "--input-file", help="input filename")
    ] = "POSCAR"
    output_filename: Annotated[
        str,
        typer.Option(
            "-of", "--output_filename", help="output filename : INCAR, POTCAR, KPOINTS."
        ),
    ] = None # type: ignore
    sp_symprec: Annotated[
        float,
        typer.Option("-ss", "--sp-symprec", help="symmetry precision for spacegroup"),
    ] = 1e-5
    lattice_type: Annotated[
        str,
        typer.Option(
            "-lt",
            "--lattice-type",
            help="lattice_type : hexagonal, tetragonal, orthorhombic",
        ),
    ] = "hexagonal"
    kpoints_type: Annotated[
        str,
        typer.Option(
            "-kt",
            "--kpoints-type",
            click_type=click.Choice(["gamma", "monkhorst", "line"]),
        ),
    ] = "gamma"
    kpoint_grid: Annotated[
        tuple[int, int, int],
        typer.Option(
            "-kg",
            "--kpoint-grid",
            help="kpoints mesh",
        ),
    ] = (12, 12, 1)
    auto_mode: Annotated[
        bool, typer.Option("-am", "--auto-mode", help="seekpath seek kpoints path")
    ] = True
    kpoint_path: Annotated[
        str, typer.Option("-kp", "--kpoint-path", help="kpoints path")
    ] = ""
    kpoint_num: Annotated[
        int, typer.Option("-kn", "--kpoint-num", help="number of kpoints")
    ] = 50
    show: Annotated[
        bool, typer.Option("-s", "--show", help="only show high symmetry points")
    ] = False
    interactive: Annotated[
        bool, typer.Option("-i", "--interactive", help="enable interactive mode", is_flag=True)
    ] = False

