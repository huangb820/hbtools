from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sys

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import figure

    # from ..cli import utils as cliutils
    from . import common_params

import matplotlib as mpl


class MyCustomNormalize(mpl.colors.Normalize):
    """
    Modified from https://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
    """

    def __init__(self, vmin, vmax, midpoint=0.0, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        import numpy as np

        normalized_min = (
            max(
                0,
                1
                / 2
                * (1 - abs((self.midpoint - self.vmin) / (self.midpoint - self.vmax))),
            )
            if (self.midpoint != self.vmax)
            else 0
        )
        normalized_max = (
            min(
                1,
                1
                / 2
                * (1 + abs((self.vmax - self.midpoint) / (self.midpoint - self.vmin))),
            )
            if (self.midpoint != self.vmin)
            else 1.0
        )
        normalized_mid = 0.5
        x, y = (
            [self.vmin, self.midpoint, self.vmax],
            [normalized_min, normalized_mid, normalized_max],
        )
        return np.ma.masked_array(np.interp(value, x, y))


class AxesSet:
    def __init__(self, ax: "plt.Axes", params: "common_params.FigSetBase"):
        self.ax = ax
        self.params = params
        self.set_title()
        self.set_labels()
        self.set_xticks()
        self.set_yticks()
        self.set_lims()
        self.hide_ticks()

    def set_title(self):
        self.ax.set_title(self.params.title) if self.params.title is not None else ...
        ...

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
        im,
        fig: "figure.Figure",
        ax: "plt.Axes",
        params: "common_params.HeatFigBase",
        vmin: float,
        vmax: float,
    ) -> None:
        import colorcet  # noqa: F401

        self.fig = fig
        self.ax = ax
        self.params = params
        if self.params.vrange is not None:
            self.vmin, self.vmax = self.params.vrange
        else:
            self.vmin, self.vmax = vmin, vmax
        self.vcenter = self.params.vcenter
        self.im = im

        ##
        self.set_norm()
        self.im.set_cmap(self.params.cmap)
        if self.params.colorbar:
            self.plot_colorbar()

    def set_norm(self):
        if self.params.norm == "Normal":
            norm = mpl.colors.Normalize(self.vmin, self.vmax)
        elif self.params.norm == "Logarithmic":
            if self.vmin < 0:
                print("Logarithmic Normalization doesn't support negative values")
                sys.exit()
            norm = mpl.colors.LogNorm(self.vmin, self.vmax)
        elif self.params.norm == "Centered":
            norm = mpl.colors.CenteredNorm(self.vcenter)
        elif self.params.norm == "SymmetricLogarithmic":
            norm = mpl.colors.SymLogNorm(
                linthresh=self.params.symlogparm[0],
                linscale=self.params.symlogparm[1],
                vmin=self.vmin,
                vmax=self.vmax,
            )
        elif self.params.norm == "TwoSlopeNorm":
            norm = mpl.colors.TwoSlopeNorm(self.vmin, self.vcenter, self.vmax)
        elif self.params.norm == "PowerLaw":
            norm = mpl.colors.PowerNorm(self.params.power, self.vmin, self.vmax)
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
            print("must have same length!")
            sys.exit()

        cbar.set_ticks(cticks)
        cbar.set_ticklabels(cticklabels)

        cbar.ax.set_ylim(self.vmin, self.vmax)


def save_show(params: "common_params.FigSetBase"):
    import matplotlib.pyplot as plt

    for savefile in params.save.split():
        plt.savefig(savefile)
    if params.show:
        plt.show()


def dorotation(x_mesh, y_mesh, rot_deg: float = 0.0):
    """
    Generate a meshgrid and rotate it by rot_rad radians.
    copy from https://stacjoverflow.com/questions/29708840/rotate-meshgrid-with-numpy
    """
    import numpy as np

    rot_rad = np.deg2rad(rot_deg)
    # Clocjwise, 2D rotation matrix
    RotMatrix = np.array(
        [[np.cos(rot_rad), np.sin(rot_rad)], [-np.sin(rot_rad), np.cos(rot_rad)]]
    )
    return np.einsum("ji, mni -> jmn", RotMatrix, np.dstack([x_mesh, y_mesh]))


def dorotation_points(points, rot_deg):
    import numpy as np

    rot_rad = np.deg2rad(rot_deg)
    RotMatrix = np.array(
        [[np.cos(rot_rad), np.sin(rot_rad)], [-np.sin(rot_rad), np.cos(rot_rad)]]
    )
    return [np.dot(RotMatrix, i) for i in points]


def expand_mesh(
    x_mesh: "np.ndarray", y_mesh: "np.ndarray", z_mesh: "np.ndarray", expand_factor: int
):
    import math

    import numpy as np

    def expandij(original: np.ndarray, i: int, j: int):
        x_add = np.vstack(
            [original[:, -1] - original[:, 0]] * original.shape[0]
        ).transpose()
        y_add = np.vstack([original[-1, :] - original[0, :]] * original.shape[1])
        return original + x_add * j + y_add * i

    expand_x_list = list([] for i in range(expand_factor))
    expand_y_list = list([] for i in range(expand_factor))
    expand_z_list = list([] for i in range(expand_factor))

    for i in range(math.ceil(-expand_factor / 2), math.ceil(expand_factor / 2)):
        for j in range(math.ceil(-expand_factor / 2), math.ceil(expand_factor / 2)):
            expand_x_list[i].append(expandij(x_mesh, i, j))
            expand_y_list[i].append(expandij(y_mesh, i, j))
            expand_z_list[i].append(z_mesh)

    expand_x_mesh = np.sort(np.block(expand_x_list), 0)
    expand_y_mesh = np.sort(np.block(expand_y_list), 0)
    expand_z_mesh = np.block(expand_z_list)
    return expand_x_mesh, expand_y_mesh, expand_z_mesh


def plot_from_cli_str(str_params: str, fig, ax):
    import importlib
    import shlex

    import click
    from typer.main import get_command

    params_list = shlex.split(str_params)
    params_list.extend(["--from_cli", "--dontshow"])

    info_name = params_list[0]
    args = params_list[1:]
    app = importlib.import_module(f"hbtools.{info_name}.cli").app

    # print(params_list)

    cmd: click.Command = get_command(app)
    # print(cmd.make_context(info_name, args))
    # rv = get_command(app).invoke(cmd.make_context(info_name, args))
    rv = get_command(app).invoke(cmd.make_context(info_name, args))
    rv[0](rv[1], fig, ax)


def get_2d_first_brillouin_zone(cell):
    """
    copy from http://staff.ustc.edu.cn/~zqj/posts/howto-plot-brillouin-zone/

    """

    def clockwiseangle_and_distance(point, origin=[0, 0], refvec=[0, 1]):
        """
        copy from https://stackoverflow.com/questions/41855695/sorting-list-of-two-dimensional-coordinates-by-clockwise-angle-using-python

        """
        import math

        # Vector between point and the origin: v = p - o
        vector = [point[0] - origin[0], point[1] - origin[1]]
        # Length of vector: ||v||
        lenvector = math.hypot(vector[0], vector[1])
        # If length is zero there is no angle
        if lenvector == 0:
            return -math.pi, 0
        # Normalize vector: v/||v||
        normalized = [vector[0] / lenvector, vector[1] / lenvector]
        dotprod = normalized[0] * refvec[0] + normalized[1] * refvec[1]  # x1*x2 + y1*y2
        diffprod = (
            refvec[1] * normalized[0] - refvec[0] * normalized[1]
        )  # x1*y2 - y1*x2
        angle = math.atan2(diffprod, dotprod)
        # Negative angles represent counter-clockwise angles so we need to subtract them
        # from 2*pi (360 degrees)
        if angle < 0:
            return 2 * math.pi + angle, lenvector
        # I return first the angle because that's the primary sorting criterium
        # but if two vectors have the same angle then the shorter distance should come first.
        return angle, lenvector

    import numpy as np

    cell = np.asarray(cell, dtype=float)
    cell_33 = np.block(
        [
            [cell, np.zeros((2, 1))],
            [np.zeros((1, 2)), np.eye((1))],
        ]
    )

    px, py, pz = np.tensordot(cell_33, np.mgrid[-1:2, -1:2, -1:2], axes=[0, 0])
    points = np.c_[px.ravel(), py.ravel(), pz.ravel()]

    from scipy.spatial import Voronoi

    vor = Voronoi(points)

    # bz_facets = []
    # bz_ridges = []
    bz_vertices = []

    # for rid in vor.ridge_vertices:
    #     if( np.all(np.array(rid) >= 0) ):
    #         bz_ridges.append(vor.vertices[np.r_[rid, [rid[0]]]])
    #         bz_facets.append(vor.vertices[rid])

    for pid, rid in zip(vor.ridge_points, vor.ridge_vertices):
        # WHY 13 ????
        # The Voronoi ridges/facets are perpendicular to the lines drawn between the
        # input points. The 14th input point is [0, 0, 0].
        if pid[0] == 13 or pid[1] == 13:
            # bz_ridges.append(vor.vertices[np.r_[rid, [rid[0]]]])
            # bz_facets.append(vor.vertices[rid])
            bz_vertices += rid

    bz_vertices = list(set(bz_vertices))
    vertices = [
        i[:-1] for i in vor.vertices[bz_vertices] if abs(i[2] - 0.5) < 0.0000001
    ]
    return sorted(vertices, key=clockwiseangle_and_distance)
    # return vor.vertices[bz_vertices], bz_ridges, bz_facets
