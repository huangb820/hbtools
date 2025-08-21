import itertools
import sys
from functools import cached_property
from typing import TYPE_CHECKING, final

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import figure
from matplotlib.collections import LineCollection
from numpy._core.multiarray import DATETIMEUNITS

from ...utils import plot_utils

# from .. import vasp_utils
from ..dataread import Readvaspout, ReadVasprun
from .. import vasp_utils

if TYPE_CHECKING:
    from .params import BandParams


@final
class BandPlot:
    def __init__(
        self,
        params: "BandParams",
        fig: figure.Figure,
        ax: plt.Axes,
    ):
        self.params: "BandParams" = params
        self.fig, self.ax = fig, ax

        self.fermi = (
            self.data.fermi if self.params.efermi is None else self.params.efermi
        )
        self.gaps = vasp_utils.get_gap(
            self.data.eigenvalues,
            self.fermi,
            self.data.kpoints,
            True,
        )
        self.fig_set()
        if self.params.pro_atoms_orbitals is None:
            self.plot_band()
        else:
            self.plot_proband()

        if self.params.legend:
            # copy from https://stackoverflow.com/questions/19385639/duplicate-items-in-legend-in-matplotlib
            handles, labels = self.ax.get_legend_handles_labels()
            unique = [
                (handle, label)
                for i, (handle, label) in enumerate(zip(handles, labels))
                if label not in labels[:i]
            ]
            self.ax.legend(*zip(*unique), loc="best")

    @cached_property
    def data(self) -> ReadVasprun | Readvaspout:
        if self.params.vaspfileformat == "h5":
            data = Readvaspout(self.params.file, auto_select_k=True)
        else:
            data = ReadVasprun(self.params.file, auto_select_k=True)
        if self.params.fix_order:
            data.eigenvalues = np.sort(data.eigenvalues, axis=2)

        return data

    @cached_property
    def xlist(self):
        kpoints_real = [
            np.dot(kpoint, self.data.rec_cell) for kpoint in self.data.kpoints
        ]

        length = (
            np.linalg.norm(kpoint1 - kpoint2)
            for kpoint1, kpoint2 in zip(
                kpoints_real, kpoints_real[0:1] + list(kpoints_real)[:-1]
            )
        )

        return [float(i) * np.pi * 2 for i in itertools.accumulate(length)]

    @cached_property
    def ylist(self):
        if self.params.efermi is None:
            return self.data.eigenvalues - self.data.fermi
        else:
            return self.data.eigenvalues - self.params.efermi

    def fig_set(self):
        # self.set_xticks_and_labels()
        BandAxesSet(self.ax, self.params, self.data, self.xlist)
        y_major_tick_size = mpl.rcParams["ytick.major.size"]
        self.ax.axhline(
            0,
            ls=(0, (y_major_tick_size, y_major_tick_size)),
            c="black",
            lw=mpl.rcParams["ytick.major.width"],
            zorder=0,
        )

    @cached_property
    def proarray_list(self):
        # result: list[np.ndarray] = []
        result = []
        assert self.params.pro_atoms_orbitals is not None
        for i, atom_orbital_str in enumerate(self.params.pro_atoms_orbitals):
            result.append(
                sum(
                    self.data.projected[:, atom, orbital, :, :]
                    for atom, orbital in vasp_utils.ParsePro(
                        self.data, atom_orbital_str, self.params.colors.split()[i], i
                    ).result
                )
            )  # print(ParsePro(self.data, atom_orbital_str).result

        ...
        return result

    @cached_property
    def lc(self) -> LineCollection:
        y_repeat = self.ylist.repeat(2, axis=1)
        yarray = (y_repeat[:, :-1, :] + y_repeat[:, 1:, :]) / 2
        ylist_left = yarray[:, :-1, :].transpose(0, 2, 1).reshape(-1)
        ylist_right = yarray[:, 1:, :].transpose(0, 2, 1).reshape(-1)

        x_repeat = np.array(self.xlist).repeat(2)
        xarray = (x_repeat[:-1] + x_repeat[1:]) / 2
        xlist_left = np.array(
            list(xarray[:-1]) * self.ylist.shape[0] * self.ylist.shape[2]
        )
        xlist_right = np.array(
            list(xarray[1:]) * self.ylist.shape[0] * self.ylist.shape[2]
        )

        left = np.stack((xlist_left, xlist_right), axis=1)
        right = np.stack((ylist_left, ylist_right), axis=1)

        segments = np.stack((left, right), axis=2)
        lc = LineCollection(list(segments), rasterized=True)

        return lc

    def plot_band(self):
        labels = (
            ["↑", "↓"] if self.params.labels is None else self.params.labels.split(";")
        )
        print(labels)
        if self.params.spin is None:
            for i, y in enumerate(self.ylist):
                self.ax.plot(
                    self.xlist,
                    y,
                    c=self.params.colors.split()[i],
                    zorder=2,
                    label=labels[i],
                )
        else:
            self.ax.plot(
                self.xlist,
                self.ylist[self.params.spin],
                c=self.params.colors.split()[0],
                zorder=2,
                label=labels[self.params.spin],
            )
        self.fig_set()

    def plot_proband(self):
        if self.params.pmode == 0:
            self.lc_proplot()
        elif self.params.pmode == 1:
            self.scatter_proplot()

    def scatter_proplot(self):
        scatter_xlist = np.tile(
            self.xlist, (len(self.data.projected), self.data.nbands, 1)
        ).transpose(0, 2, 1)
        assert self.params.pro_atoms_orbitals is not None

        labels = (
            self.params.pro_atoms_orbitals
            if self.params.labels is None
            else self.params.labels.split(";")
        )
        if len(labels) != len(self.proarray_list):
            print("labels must have same length with pros")
            sys.exit()
        for i, proarray in enumerate(self.proarray_list):
            if self.params.hollow:
                ec = self.params.colors.split()[i]
                fc = "white"
            else:
                ec = fc = self.params.colors.split()[i]

            if self.params.spin is not None and len(self.data.projected) == 4:
                self.ax.scatter(
                    scatter_xlist[self.params.spin],
                    self.ylist[0],
                    s=abs(proarray[self.params.spin]) * self.params.scale,
                    ec=ec,
                    fc=fc,
                    label=labels[i],
                )
            elif self.params.spin is not None and len(self.data.projected) != 4:
                self.ax.scatter(
                    scatter_xlist[self.params.spin],
                    self.ylist[self.params.spin],
                    s=proarray[self.params.spin] * self.params.scale,
                    ec=ec,
                    fc=fc,
                    label=labels[i],
                )
            elif self.params.spin is None and len(self.data.projected) == 4:
                self.ax.scatter(
                    scatter_xlist[0],
                    self.ylist[0],
                    s=proarray[0] * self.params.scale,
                    ec=ec,
                    fc=fc,
                    label=labels[i],
                )
            else:
                self.ax.scatter(
                    scatter_xlist,
                    self.ylist,
                    s=proarray * self.params.scale,
                    ec=ec,
                    fc=fc,
                    label=labels[i],
                )

    def lc_proplot(self):
        if len(self.proarray_list) > 1:
            print("LineCollection only support 1 pro")
            sys.exit()
        proarray = self.proarray_list[0]

        if self.params.spin is not None:
            proarray = proarray[self.params.spin : self.params.spin + 1]
        elif len(self.data.projected) == 2:
            proarray[1] = -proarray[1]
        else:
            proarray = proarray[0:1, :, :]

        points_repeat = proarray.repeat(2, axis=1)[:, 1:-1, :]
        lc_array = points_repeat.transpose(0, 2, 1).reshape(-1)
        if self.params.vrange is None:
            pmin = lc_array.min()
            pmax = lc_array.max()
        else:
            pmin, pmax = self.params.vrange

        self.lc.set_array(lc_array)
        plot_utils.HeatSet(self.lc, self.fig, self.ax, self.params, pmin, pmax)
        self.lc.set_capstyle("round")
        self.ax.add_collection(self.lc)


class BandAxesSet(plot_utils.AxesSet):
    def __init__(self, ax: plt.Axes, parmas: "BandParams", data, xlist):
        self.xlist = xlist
        self.data = data
        super().__init__(ax, parmas)

    def set_xticks(self):
        def symbol_to_latex(symbol: str) -> str:
            if symbol[0] not in [chr(i) for i in range(65, 91)] + [
                chr(i) for i in range(97, 123)
            ] and (symbol[0] != "$" and symbol[-1] != "$"):
                return f"${symbol}$"
            else:
                return symbol

        def handle_kpoint_labels(klist: list[str]) -> list[str]:
            result = []
            result.append(symbol_to_latex(klist[0]))
            for k1, k2 in zip(klist[2::2], klist[1:-1:2]):
                k1, k2 = symbol_to_latex(k1), symbol_to_latex(k2)
                if k1 == k2:
                    result.append(k1)
                else:
                    result.append(f"{k2}/{k1}")
            result.append(klist[-1])
            return result

        if self.params.xticks is not None:
            xticks = [self.xlist[int(i)] for i in self.params.xticks.split()]
        else:
            if self.data.kpoints_division is None:
                # TODO
                xticks = []
            else:
                xticks = ([0.0] + self.xlist)[:: self.data.kpoints_division]
        if self.params.xticklabels is not None:
            xticklabels = self.params.xticklabels.split()
        else:
            if self.data.labels_kpoints is None or self.data.labels_kpoints == []:
                xticklabels = []
            else:
                xticklabels = handle_kpoint_labels(self.data.labels_kpoints)
        assert len(xticks) == len(xticklabels)
        self.ax.set_xticks(xticks)
        self.ax.set_xticklabels(xticklabels)
        for i in xticks:
            self.ax.axvline(
                i, c="lightgrey", zorder=1, lw=mpl.rcParams["ytick.major.width"]
            )

    def set_lims(self):
        assert self.params.xrange is not None
        self.ax.set_xlim(
            self.xlist[self.params.xrange[0]], self.xlist[self.params.xrange[1]]
        )
        self.ax.set_ylim(*self.params.yrange) if self.params.yrange is not None else ...
