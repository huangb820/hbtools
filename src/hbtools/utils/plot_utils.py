from pathlib import Path
from typing import cast

from matplotlib import axes, colors, figure
from matplotlib.cm import ScalarMappable
from matplotlib.backend_bases import KeyEvent

from typing_extensions import override

from .common_params import FigSetBase, HeatFigBase


class MyCustomNormalize(colors.Normalize):
    """
    Modified from https://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
    """

    def __init__(
        self, vmin: float, vmax: float, midpoint: float = 0.0, clip: bool = False
    ):
        self.midpoint: float = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    @override
    def __call__(self, value: float, clip: bool | None = None):  # type:ignore
        vmin = cast(float, self.vmin)
        vmax = cast(float, self.vmax)
        import numpy as np

        if vmin == vmax:
            return np.full_like(value, 0.5, dtype=np.float64)
        midpoint = self.midpoint

        normalized_min = (
            max(
                0,
                1 / 2 * (1 - abs((midpoint - vmin) / (midpoint - vmax))),
            )
            if (self.midpoint != self.vmax)
            else 0
        )
        normalized_max = (
            min(
                1,
                1 / 2 * (1 + abs((vmax - midpoint) / (midpoint - vmin))),
            )
            if (self.midpoint != self.vmin)
            else 1.0
        )
        normalized_mid = 0.5
        x, y = (
            np.array([self.vmin, self.midpoint, self.vmax]),
            [normalized_min, normalized_mid, normalized_max],
        )
        return np.ma.masked_array(np.interp(value, x, y))


class AxesSet:
    def __init__(self, ax: axes.Axes, params: FigSetBase):
        self.ax: axes.Axes = ax
        self.params: FigSetBase = params
        self.set_title()
        self.set_labels()
        self.set_xticks()
        self.set_yticks()
        self.set_lims()
        self.hide_ticks()

    def set_title(self):
        self.ax.set_title(self.params.title) if self.params.title is not None else ...

    def set_labels(self):
        self.ax.set_xlabel(
            self.params.xlabel
        ) if self.params.xlabel is not None else ...
        self.ax.set_ylabel(
            self.params.ylabel
        ) if self.params.ylabel is not None else ...

    def set_lims(self):
        self.ax.set_xlim(*self.params.xrange) if self.params.xrange is not None else ...
        self.ax.set_ylim(*self.params.yrange) if self.params.yrange is not None else ...

    def set_xticks(self):
        from matplotlib.ticker import AutoLocator, AutoMinorLocator

        self.ax.set_xticks(
            [float(i) for i in self.params.xticks.split()]
        ) if self.params.xticks is not None else self.ax.xaxis.set_major_locator(
            AutoLocator()
        )
        self.ax.set_xticklabels(
            self.params.xticklabels
        ) if self.params.xticklabels is not None else ...
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())

    def set_yticks(self):
        from matplotlib.ticker import AutoLocator, AutoMinorLocator

        self.ax.set_yticks(
            [float(i) for i in self.params.yticks.split()]
        ) if self.params.yticks is not None else self.ax.yaxis.set_major_locator(
            AutoLocator()
        )
        self.ax.set_yticklabels(
            self.params.yticklabels
        ) if self.params.yticklabels is not None else ...
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())

    def hide_ticks(self):
        if self.params.hide_xticks:
            self.ax.tick_params(which="both", bottom=False)
        if self.params.hide_yticks:
            self.ax.tick_params(which="both", left=False)


class HeatSet:
    def __init__(
        self,
        im: ScalarMappable,
        # im: AxesImage | QuadMesh | ScalarMappable,
        fig: figure.Figure,
        ax: axes.Axes,
        params: HeatFigBase,
        vmin: float,
        vmax: float,
    ) -> None:
        self.fig: figure.Figure = fig
        self.ax: axes.Axes = ax
        self.params: "HeatFigBase" = params
        self.vmin: float
        self.vmax: float
        if self.params.vrange is not None:
            self.vmin, self.vmax = self.params.vrange
        else:
            self.vmin, self.vmax = vmin, vmax
        self.vcenter: float = self.params.vcenter
        self.im = im
        self.set_norm()
        self.im.set_cmap(self.params.cmap)
        if self.params.colorbar:
            self.plot_colorbar()

    def set_norm(self):
        if self.params.norm == "Normal":
            norm = colors.Normalize(self.vmin, self.vmax)
        elif self.params.norm == "Logarithmic":
            if self.vmin < 0:
                raise ValueError(
                    "Logarithmic Normalization doesn't support negative values"
                )
            norm = colors.LogNorm(self.vmin, self.vmax)
        elif self.params.norm == "Centered":
            norm = colors.CenteredNorm(self.vcenter)
        elif self.params.norm == "SymmetricLogarithmic":
            norm = colors.SymLogNorm(
                linthresh=self.params.symlogparm[0],
                linscale=self.params.symlogparm[1],
                vmin=self.vmin,
                vmax=self.vmax,
            )
        elif self.params.norm == "TwoSlopeNorm":
            norm = colors.TwoSlopeNorm(
                vmin=self.vmin, vcenter=self.vcenter, vmax=self.vmax
            )
        elif self.params.norm == "PowerLaw":
            norm = colors.PowerNorm(self.params.power, self.vmin, self.vmax)
        else:
            norm = MyCustomNormalize(self.vmin, self.vmax, self.vcenter)
        self.im.set_norm(norm)

    def plot_colorbar(self):
        cbar = self.fig.colorbar(self.im, ax=self.ax)
        if self.params.cticks is not None:
            cticks = [float(i) for i in self.params.cticks.split()]
        elif self.vmin < 0 and self.vmax > 0:
            cticks = [self.vmin, self.vmin / 2, 0, self.vmax / 2, self.vmax]
        else:
            cticks = [
                self.vmin,
                (self.vmin + self.vmax) * 1 / 4,
                (self.vmin + self.vmax) / 2,
                (self.vmin + self.vmax) * 3 / 4,
                self.vmax,
            ]

        if self.params.cticklabels is not None:
            cticklabels = self.params.cticklabels.split()

        else:
            cticklabels: list[str] = [f"{i:.2f}" for i in cticks]

        if len(cticks) != len(cticklabels):
            raise ValueError("cticks and cticklabels must have same length")

        cbar.set_ticks(cticks)
        cbar.set_ticklabels(cticklabels)

        cbar.ax.set_ylim(self.vmin, self.vmax)


class FigPlotBase:
    def __init__(self, params: FigSetBase, fig: figure.Figure, ax: axes.Axes): ...


def set_style(rc_file: Path | None = None):
    from importlib import resources

    import matplotlib as mpl

    if rc_file is None or not rc_file.exists():
        with resources.path("hbtools", "matplotlibrc") as rc_path:
            if rc_path.exists():
                mpl.rc_file(rc_path)
    else:
        mpl.rc_file(rc_file)


def render_and_save(
    plot_cls: type[FigPlotBase],
    params: FigSetBase,
    fig: figure.Figure | None,
    ax: axes.Axes | None,
):
    import matplotlib.pyplot as plt

    if params.from_cli is False:
        return (plot_cls, params)

    if fig is None and ax is None:
        fig, ax = plt.subplots()
    if fig is None or ax is None:
        raise ValueError("must set fig and ax")

    plot_cls(params, fig, ax)
    for savefile in params.save.split():
        plt.savefig(savefile)
    if params.show:
        plt.show()


def plot_from_cli_str(str_params: str, fig: figure.Figure, ax: axes.Axes):
    import importlib
    import shlex

    import click
    from typer.main import get_command

    params_list = shlex.split(str_params)
    params_list.extend(["--from_cli", "--dontshow"])

    info_name = params_list[0]
    args = params_list[1:]
    module = importlib.import_module(f"hbtools.{info_name}.cli")
    app = getattr(module, "app")

    cmd: click.Command = get_command(app)
    # print(cmd.make_context(info_name, args))
    # rv = get_command(app).invoke(cmd.make_context(info_name, args))
    rv = get_command(app).invoke(cmd.make_context(info_name, args))
    rv[0](rv[1], fig, ax)


def plot_series(plot_cls: type[FigPlotBase], params: FigSetBase):
    from pathlib import Path

    set_style(params.matplotlibrc)

    import matplotlib.pyplot as plt

    files = list(Path(".").rglob(params.file))
    if len(files) == 0:
        raise ValueError("No files found. Ensure the file is correct.")
    elif len(files) == 1:
        return render_and_save(plot_cls, params, None, None)

    else:
        if not params.from_cli:
            raise ValueError("Do not specify multiple files in script mode.")

    savedir = Path(params.save) if params.save != "" else None
    params.save = ""

    if params.show:
        params.show = False
        current_index = 0
        num_figures = len(files)
        path_title =True
        fig, ax = plt.subplots()

        def update_figure(files: list[Path], params: "FigSetBase", index: int,path_title:bool):
            params.file = str(files[index])
            ax.clear()
            render_and_save(plot_cls, params, fig, ax)
            if path_title == True:
                ax.set_title(f"{params.file}")

        update_figure(files, params, 0,path_title)

        fig.canvas.draw()

        def on_key(event: KeyEvent):
            nonlocal current_index, path_title
            if event.key in ["right", "down", "j", "l"]:
                current_index = (current_index + 1) % num_figures
            elif event.key in ["left", "up", "k", "h"]:
                current_index = (current_index - 1) % num_figures
            elif event.key =="t":
                path_title = not path_title
            else:
                return

            update_figure(files, params, current_index,path_title)
            fig.canvas.draw()

        fig.canvas.mpl_connect("key_press_event", on_key)  # type: ignore

        plt.show()
    if savedir is not None:
        from tqdm import tqdm

        savedir.mkdir(exist_ok=True)
        for file in tqdm(files, desc="Saving figures"):
            params.file = str(file)
            params.save = f"{savedir}/{file}.png"
            render_and_save(plot_cls, params, None, None)
