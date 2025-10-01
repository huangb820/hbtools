import itertools
import sys

import numpy as np
import numpy.typing as npt
from numpy.typing import NDArray
import rich
from rich.panel import Panel

from .dataread import VaspData


def get_gap(
    eigenvalues: npt.NDArray[np.floating],
    fermi: float,
    kpoints: np.ndarray,
    stdout: bool = False,
    vbms: list[int] | None = None,
) -> list[float]:
    def is_metal_or_vbm(ylist: np.ndarray) -> bool | int:
        nbands = ylist.shape[1]
        extremum = np.array(
            [[ylist[:, n].min(), ylist[:, n].max()] for n in range(nbands)]
        )

        if (extremum[:, 0] * extremum[:, 1]).min() > 0:
            maxs = extremum[:, 1]
            vbm = int(np.count_nonzero(abs(maxs) - maxs))
            return vbm
        else:
            return True

    def get_kpoints_vbm(ylist: np.ndarray, kpoints: np.ndarray):
        index = np.where(ylist == ylist.max())
        return kpoints[index]

    def get_kpoints_cbm(ylist: np.ndarray, kpoints: np.ndarray):
        index = np.where(ylist == ylist.min())
        return kpoints[index]

    ylist = eigenvalues - fermi
    gaps: list[float] = []
    std_str = ""

    if stdout:
        std_str += f"Fermi Level is [blue]{fermi:6f} (eV)[/blue]\n"

    for i, spin in enumerate(ylist):
        vbm = is_metal_or_vbm(spin) if vbms is None else vbms[i]
        if stdout:
            std_str += f"[yellow]{'=' * 30} {i + 1}th spin {'=' * 30} [/yellow]\n"
        if vbm is True:
            gaps.append(0.0)
            if stdout:
                std_str += "Fermi level intersects energy bands, [blue]Metal[/blue]\n"
        else:
            e_vbm = float(spin[:, vbm - 1].max())
            k_vbm = get_kpoints_vbm(spin[:, vbm - 1], kpoints)
            vbm_energy = spin[:, vbm - 1].max() + fermi
            cbm_energy = spin[:, vbm].min() + fermi
            e_cbm = float(spin[:, vbm].min())
            k_cbm = get_kpoints_cbm(spin[:, vbm], kpoints)
            gap = e_cbm - e_vbm
            if gap <= 0:
                gaps.append(0.0)
                if stdout:
                    std_str += (
                        "Fermi level intersects energy bands, [blue]Metal[/blue]\n"
                    )

            else:
                gaps.append(gap)
                if stdout:
                    std_str += f"vbm locates at{k_vbm} of [red]{vbm}th[/red] band, vbm energy is [orange1]{vbm_energy:.6f} eV[/orange1]\n"

                    std_str += f"cbm locates at {k_cbm} of [red]{vbm + 1}th[/red] band, cbm energy is [orange1]{cbm_energy:.6f}[/orange1] eV\n"
                    std_str += f"band gap is {gap}\n"
    if stdout:
        rich.print(Panel(std_str))

    return gaps


def get_valley_polarization(
    eigenvalues: NDArray[np.float64],
    fermi: float = 0.0,
    vbms: list[int] | None = None,
    point1: int = 49,
    point2: int = 149,
):
    def is_metal_or_vbm(ylist: NDArray[np.float64]) -> bool | int:
        nbands = ylist.shape[1]
        extremum = np.array(
            [[ylist[:, n].min(), ylist[:, n].max()] for n in range(nbands)]
        )

        if (extremum[:, 0] * extremum[:, 1]).min() > 0:
            maxs = extremum[:, 1]
            vbm = np.count_nonzero(abs(maxs) - maxs)
            return int(vbm)
        else:
            return True

    eigenvalues = eigenvalues
    ylist = eigenvalues - fermi

    for i, spin in enumerate(ylist):
        vbm = is_metal_or_vbm(spin) if vbms is None else vbms[i]
        value1: float = spin[point1, vbm - 1]
        rich.print(f"Energy at point {point1} of band {vbm} is {value1:.6f} eV")
        value2: float = spin[point2, vbm - 1]
        rich.print(f"Energy at point {point2} of band {vbm} is {value2:.6f} eV")

        rich.print(f"valley polarization is {value2 - value1:.6f} eV")


orbitals_str_all = (
    "s py pz px dxy dyz dz2 dxz dx2-y2 fy3x2 fxyz fyz2 fz3 fxz2 fzx2 fx3".split()
)


class ParsePro:
    def __init__(
        self,
        data: VaspData,
        atom_orbital_str: str,
        color: str,
        index: int,
    ):
        self.__data: VaspData = data
        self.__orbital_str_all = orbitals_str_all[0 : self.__data.orbital_num]
        self.result, self.result_str = self.handle(atom_orbital_str)
        test = Panel(
            self.result_str,
            title=f"projected atoms and orbitals of your choice for index {index}",
            title_align="left",
            style=color,
        )
        rich.print(test)

    def handle(self, atom_orbital_strs: str) -> tuple[list[tuple[int, int]], str]:
        result: list[tuple[int, int]] = []
        result_str_list: list[str] = []
        for atom_orbital_str in atom_orbital_strs.split(";"):
            ao_list, ao_str = self.__parse_atom_orbital(atom_orbital_str)
            result.extend(ao_list)
            result_str_list.append(ao_str)

        if len(set(result)) != len(result):
            print(
                "The projection  you selected contains duplicate orbitals. Please choose again."
            )
            sys.exit()
        return (result, " + ".join(result_str_list))

    def __parse_atom_orbital(
        self, atom_orbital_str: str
    ) -> tuple[list[tuple[int, int]], str]:
        if len(atom_orbital_str.split(":")) != 2:
            print(f"can't parse {atom_orbital_str}, check it!")
            sys.exit()
        atom_str, orbital_str = (i.strip() for i in atom_orbital_str.split(":"))
        atom_list, atom_str = self.__handle_atom_str(atom_str)
        orbital_list, orbital_str = self.__handle_orbital_str(orbital_str)
        atom_orbital_list = list(itertools.product(atom_list, orbital_list))
        atom_orbital_str = f"orbital {orbital_str} of atom {atom_str}"
        return (atom_orbital_list, atom_orbital_str)

    def __handle_atom_str(self, atom_str: str) -> tuple[list[int], str]:
        try:
            return (
                [int(atom_str)],
                f"{self.__data.symbols[int(atom_str)]}{int(atom_str)}",
            )
        except ValueError:
            if atom_str == "all":
                return (list(range(self.__data.ionnum)), atom_str)
            atoms_list = [i for i, x in enumerate(self.__data.symbols) if x == atom_str]
            if atoms_list == []:
                print(f"{atom_str} is not in the list {self.__data.symbols}, check it!")
                sys.exit()
            return (atoms_list, atom_str)

    def __handle_orbital_str(self, orbital_str: str) -> tuple[list[int], str]:
        try:
            return ([int(orbital_str)], self.__orbital_str_all[int(orbital_str)])
        except ValueError:
            if orbital_str == "all":
                return (list(range(self.__data.orbital_num)), orbital_str)
            elif orbital_str == "p" and self.__data.orbital_num >= 4:
                return ([1, 2, 3], "p")

            elif orbital_str == "d" and self.__data.orbital_num >= 9:
                return ([4, 5, 6, 7, 8], "d")

            elif orbital_str == "f" and self.__data.orbital_num >= 16:
                return ([9, 10, 11, 12, 13, 14, 15], "f")
            else:
                orbitals_list = [
                    i for i, x in enumerate(self.__orbital_str_all) if x == orbital_str
                ]
                if orbitals_list == []:
                    print(
                        f"{orbital_str} is not in the list {self.__orbital_str_all}, check it!"
                    )
                    sys.exit()
                return (orbitals_list, orbital_str)
