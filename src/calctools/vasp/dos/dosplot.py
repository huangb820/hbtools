import sys
from functools import cached_property

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import figure
from matplotlib.patches import Polygon

from calctools.utils.plot_utils import AxesSet
from .. import vasp_utils
from ..dataread import Readvaspout, ReadVasprun
from .params import DosParams


def fillplot(x, y, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    ax.fill(x, y, **kwargs)


def lineplot(x, y, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    ax.plot(x, y, **kwargs)


# copy from https://stackoverflow.com/questions/29321835/is-it-possible-to-get-color-gradients-under-curve-in-matplotlib
def gradient_fill(x, y, ax=None, fill_color=None, **kwargs):
    """
    Plot a line with a linear alpha gradient filled beneath it.

    Parameters
    ----------
    x, y : array-like
        The data values of the line.
    fill_color : a matplotlib color specifier (string, tuple) or None
        The color for the fill. If None, the color of the line will be used.
    ax : a matplotlib Axes instance
        The axes to plot on. If None, the current pyplot axes will be used.
    Additional arguments are passed on to matplotlib's ``plot`` function.

    Returns
    -------
    line : a Line2D instance
        The line plotted.
    im : an AxesImage instance
        The transparent gradient clipped to just the area beneath the curve.
    """
    if ax is None:
        ax = plt.gca()

    (line,) = ax.plot(x, y, **kwargs)
    if fill_color is None:
        fill_color = line.get_color()

    zorder = line.get_zorder()
    alpha = line.get_alpha()
    alpha = 1.0 if alpha is None else alpha

    z = np.empty((100, 1, 4), dtype=float)
    rgb = mcolors.colorConverter.to_rgb(fill_color)
    z[:, :, :3] = rgb
    z[:, :, -1] = np.linspace(0, alpha, 100)[:, None]
    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    if ymin < 0:
        ymin, ymax = ymax, ymin
    im = ax.imshow(
        z, aspect="auto", extent=[xmin, xmax, ymin, ymax], origin="lower", zorder=zorder
    )

    xy = np.column_stack([x, y])
    xy = np.vstack([[xmin, ymin], xy, [xmax, ymin], [xmin, ymin]])
    clip_path = Polygon(xy, facecolor="none", edgecolor="none", closed=True)
    ax.add_patch(clip_path)
    im.set_clip_path(clip_path)

    ax.autoscale(True)
    return line, im


class DosPlot:
    def __init__(
        self,
        params: "DosParams",
        fig: figure.Figure,
        ax: plt.Axes,
    ):
        self.params, self.fig, self.ax = params, fig, ax
        self.fig_set()
        self.plot_tdos()
        if self.params.pro_atoms_orbitals is not None:
            self.plot_prodos()
        if self.params.legend:
            self.ax.legend(loc="best")

    @cached_property
    def data(self) -> ReadVasprun | Readvaspout:
        if self.params.vaspfileformat == "h5":
            data = Readvaspout(self.params.file)
        else:
            data = ReadVasprun(self.params.file)
        return data

    @cached_property
    def xlist(self) -> np.ndarray:
        if self.params.efermi is None:
            return self.data.dose - self.data.fermi
        else:
            return self.data.dose - self.params.efermi

    @cached_property
    def total_dos(self) -> np.ndarray:
        return self.data.dos

    @cached_property
    def pdos_list(self):
        # result: list[np.ndarray] = []
        result = []
        assert self.params.pro_atoms_orbitals is not None

        for i, atom_orbital_str in enumerate(self.params.pro_atoms_orbitals):
            result.append(
                sum(
                    self.data.dospar[:, atom, orbital, :]
                    for atom, orbital in vasp_utils.ParsePro(
                        self.data, atom_orbital_str, self.params.colors.split()[i], i
                    ).result
                )
            )
        return result

    def __plotdos(self, dos, **kwargs):
        if self.params.pmode == 1:
            plot = lineplot
        elif self.params.pmode == 2:
            plot = fillplot
        else:
            plot = gradient_fill

        if self.params.spin is not None:
            plot(self.xlist, dos[self.params.spin], **kwargs)
        elif len(self.total_dos) == 2:
            plot(self.xlist, dos[0], **kwargs)
            kwargs.pop("label")
            plot(self.xlist, -dos[1], **kwargs)
        else:
            plot(self.xlist, dos[0], **kwargs)

    def plot_tdos(self):
        if self.params.tdos:
            tlabel = (
                self.params.tdos_label if self.params.tdos_label is not None else "TDOS"
            )
            self.__plotdos(
                self.total_dos,
                ax=self.ax,
                color=self.params.tcolor,
                zorder=2,
                label=tlabel,
            )

    def plot_prodos(self):
        assert self.params.pro_atoms_orbitals is not None
        labels = (
            self.params.pro_atoms_orbitals
            if self.params.labels is None
            else self.params.labels.split(";")
        )
        if len(labels) != len(self.pdos_list):
            print("labels must have same length with pros")
            sys.exit()
        for i, pdos in enumerate(self.pdos_list):
            self.__plotdos(
                pdos,
                ax=self.ax,
                color=self.params.colors.split()[i],
                zorder=4,
                label=labels[i],
            )

    def fig_set(self):
        AxesSet(self.ax, self.params)
