from pathlib import Path
from typing import Annotated
import click
import typer

from ..utils.cli_utils import dataclass_cli
from .band.params import BandParams
from .dos.params import DosParams

app = typer.Typer(no_args_is_help=True)


@app.command("band")
@dataclass_cli
def band(params: BandParams):
    print(params)
    from ..utils import plot_utils
    from .band.bandplot import BandPlot

    if params.from_cli is False:
        return (BandPlot, params)

    import matplotlib

    matplotlib.use("qtagg")
    import matplotlib.pyplot as plt

    from matplotlib.figure import Figure
    from matplotlib.axes import Axes

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()
    _ = BandPlot(params, fig, ax)
    plot_utils.save_show(params)


@app.command("dos")
@dataclass_cli
def dos(
    params: DosParams,
):
    from ..utils import plot_utils
    from .dos.dosplot import DosPlot

    import matplotlib

    matplotlib.use("qtagg")
    if params.from_cli is False:
        return (DosPlot, params)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    DosPlot(params, fig, ax)
    plot_utils.save_show(params)


@app.command("nbands_ewin")
def nbands_ewin(
    energy_windows: Annotated[
        tuple[float, float], typer.Option("--energy_windows", "-ew")
    ],
    vaspfileformat: Annotated[
        str,
        typer.Option(
            "-vf",
            "--vaspfileformat",
            click_type=click.Choice(["h5", "xml"]),
            envvar="MXMF_VASPFILE_FORMAT",
            help="read file format.",
        ),
    ] = "h5",
    file: Annotated[Path, typer.Argument(exists=True)] = Path("vaspout.h5"),
    fermi: Annotated[float, typer.Option("--fermi", "-f")] = 0,
    spin: Annotated[int, typer.Option("--spin", "-s", min=0, max=1)] = 0,
):
    from .dataread import Readvaspout, ReadVasprun
    import rich

    if vaspfileformat == "h5":
        eigenvalues = Readvaspout(file).eigenvalues[spin]
    else:
        eigenvalues = ReadVasprun(file).eigenvalues[spin]

    emin, emax = energy_windows
    band_max = eigenvalues.max(axis=0)
    band_min = eigenvalues.min(axis=0)
    band_out = 0
    band_in = 0
    for b_min, b_max in zip(band_min, band_max):
        if b_min > emin and b_max < emax:
            band_in += 1
        elif (b_min < emin and b_max > emin) or (b_min < emax and b_max > emax):
            band_out += 1
    rich.print(
        f"the num of bands fully in your give energy window for spin {spin} is [orange1]{band_in}"
    )
    rich.print(
        f"the num of bands partly in your give energy window for spin {spin} is [orange1]{band_out}"
    )


@app.command("gap")
def gap(
    file: Annotated[Path, typer.Argument(exists=True)] = Path("vaspout.h5"),
    vaspfileformat: Annotated[
        str,
        typer.Option(
            "-vf",
            "--vaspfileformat",
            click_type=click.Choice(["h5", "xml"]),
            envvar="MXMF_VASPFILE_FORMAT",
            help="read file format.",
        ),
    ] = "h5",
    vbms_str: Annotated[
        str | None,
        typer.Option(
            "--vbms",
            "-v",
        ),
    ] = None,
):
    from .dataread import Readvaspout, ReadVasprun
    from ..vasp.vasp_utils import get_gap

    if vaspfileformat == "h5":
        data = Readvaspout(file)
    else:
        data = ReadVasprun(file)

    if vbms_str is not None:
        vbms = [int(i) for i in vbms_str.split()]
    else:
        vbms = None
    get_gap(data.eigenvalues, data.fermi, data.kpoints, True, vbms)
