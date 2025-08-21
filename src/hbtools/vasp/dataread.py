from functools import cached_property
from pathlib import Path
from typing import final

import h5py
import numpy as np
import numpy.typing as npt
from lxml.etree import parse


@final
class Readvaspout:
    def __init__(
        self,
        file: str | Path = "vaspout.h5",
        opt: bool | None = None,
        auto_select_k: bool = False,
    ):
        self.file = h5py.File(file, "r")
        if opt is True or (
            opt is None and self.file.get("input/kpoints_opt") is not None
        ):
            self.prefix1, self.prefix2 = "_opt", "_kpoints_opt"
        else:
            self.prefix1, self.prefix2 = "", ""
        if auto_select_k:
            self.k_index = np.where(self.weights == 0)[0]
            if list(self.k_index) == []:
                self.k_index = np.where(self.weights > 0)[0]
        else:
            self.k_index = np.where(self.weights >= 0)[0]

    @cached_property
    def labels_kpoints(self) -> list[str] | None:
        labels = self.file.get(f"input/kpoints{self.prefix1}/labels_kpoints")
        if labels is None:
            return None
        labels_array = np.array(labels)
        xticklabels = [i.decode("utf8") for i in labels_array]
        return xticklabels

    @cached_property
    def kpoints_division(self) -> int | None:
        mode = self.file.get(f"input/kpoints{self.prefix1}/mode")
        if np.array(mode) == b"l":
            return int(
                np.array(self.file.get(f"input/kpoints{self.prefix1}/number_kpoints"))
            )
        return None

    @cached_property
    def symbols(self) -> list[str]:
        ion_types = np.array(self.file.get("results/positions/ion_types"))
        number_ion_types = np.array(self.file.get("results/positions/number_ion_types"))
        symbols = []
        for i, ion in enumerate(ion_types):
            symbols.extend([ion.decode("utf-8")] * number_ion_types[i])
        return symbols

    @cached_property
    def nedos(self) -> int:
        n = np.array(self.file.get("results/electron_dos/nedos"))
        return int(n)

    @cached_property
    def ionnum(self) -> int:
        ionnum = np.array(self.file.get("results/positions/number_ion_types")).sum()
        return ionnum

    @cached_property
    def positions(self) -> npt.NDArray[np.float64]:
        position = np.array(self.file.get("results/positions/position_ions"))
        return position

    @cached_property
    def real_cell(self) -> npt.NDArray[np.float64]:
        real_cell = np.array(self.file.get("results/positions/lattice_vectors"))
        return real_cell

    @cached_property
    def rec_cell(self) -> npt.NDArray[np.float64]:
        rec_cell = np.zeros((3, 3))
        volume = np.dot(
            np.cross(self.real_cell[:, 0], self.real_cell[:, 1]),
            self.real_cell[:, 2],
        )
        rec_cell[:, 0] = np.cross(self.real_cell[:, 1], self.real_cell[:, 2]) / volume
        rec_cell[:, 1] = np.cross(self.real_cell[:, 2], self.real_cell[:, 0]) / volume
        rec_cell[:, 2] = np.cross(self.real_cell[:, 0], self.real_cell[:, 1]) / volume
        return rec_cell

    @cached_property
    def fermi(self) -> float:
        fermi_energy = np.array(self.file.get("results/electron_dos/efermi"))
        return float(fermi_energy)

    @cached_property
    def kpoints(self) -> npt.NDArray[np.float64]:
        kpoints = np.array(
            self.file.get(f"results/electron_eigenvalues{self.prefix2}/kpoint_coords")
        )
        return kpoints[self.k_index]

    @cached_property
    def nkpoints(self) -> int:
        return len(self.kpoints)

    @cached_property
    def weights(self) -> npt.NDArray[np.float64]:
        weights = np.array(
            self.file.get(
                f"results/electron_eigenvalues{self.prefix2}/kpoints_symmetry_weight"
            )
        )
        return weights

    @cached_property
    def nbands(self) -> int:
        nbands = np.array(
            self.file.get("results/electron_eigenvalues/eigenvalues")
        ).shape[-1]
        return nbands

    @cached_property
    def eigenvalues(self) -> npt.NDArray[np.float64]:
        eigenvalues = np.array(
            self.file.get(f"results/electron_eigenvalues{self.prefix2}/eigenvalues")
        )
        return eigenvalues[:, self.k_index, :]

    @cached_property
    def dos(self) -> npt.NDArray[np.float64]:
        dos = np.array(self.file.get("results/electron_dos/dos"))
        return dos

    @cached_property
    def orbital_num(self):
        return self.dospar.shape[2]

    @cached_property
    def dosi(self) -> npt.NDArray[np.float64]:
        """A two-dimensional array about partial dos

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first demension represents the different spins

            The second demension represents the different energies
        """
        dosi = np.array(self.file.get("results/electron_dos/dosi"))
        return dosi

    @cached_property
    def dospar(self) -> npt.NDArray[np.float64]:
        """A four-dimensional array about partial dos

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first demension represents the different spins

            The second dimension represents the different ions

            The third demension represents the energy and different orbitals

            The fourth demension represents the different energies
        """
        dospar = np.array(self.file.get("results/electron_dos/dospar"))
        return dospar

    @cached_property
    def dose(self) -> npt.NDArray[np.float64]:
        dose = np.array(self.file.get("results/electron_dos/energies"))
        return dose

    @cached_property
    def projected(self) -> npt.NDArray[np.float64]:
        """A five-dimensional array about partial dos

        Returns:
        -------
        <class 'numpy.ndarray'>

            The first dimension represents the different spins

            The second demension represents the different ions

            The third demension represents  different orbitals

            The fourth demension represents the different kpoints

            The fifth demension represents the different bands
        """
        projected = np.array(self.file.get(f"results/projectors{self.prefix2}/par"))[
            :, :, :, self.k_index, :
        ]
        return projected


class ReadVasprun:
    def __init__(self, file=Path("vasprun.xml"), auto_select_k: bool = False):
        self.file = parse(file)
        if auto_select_k:
            self.k_index = np.where(self.weights == 0)[0]
            if list(self.k_index) == []:
                print("here")
                self.k_index = np.where(self.weights > 0)[0]
        else:
            self.k_index = np.where(self.weights > 0)[0]

    @cached_property
    def kpoints_division(self) -> None:
        return None

    @cached_property
    def labels_kpoints(self) -> None:
        return None

    @cached_property
    def symbols(self):
        symbolstr = self.file.xpath("/modeling/atominfo/array[@name='atoms']/set")[
            0
        ].xpath("string(.)")
        symbols = symbolstr.split()[0:-1:2]
        return symbols

    @cached_property
    def nedos(self):
        nedos = int(
            self.file.xpath(
                "/modeling/parameters/separator[@name='dos']/i[@name='NEDOS']"
            )[0].text
        )
        return nedos

    @cached_property
    def ionnum(self):
        ionnum = int(self.file.xpath("/modeling/atominfo/atoms")[0].text)
        return ionnum

    @cached_property
    def positions(self):
        positionstr = self.file.xpath(
            "/modeling/structure[@name='finalpos']/varray[@name='positions']"
        )[0].xpath("string(.)")
        positionarray = np.array(positionstr.split(), dtype=float).reshape(-1, 3)
        return positionarray

    @cached_property
    def real_cell(self):
        basis = self.file.xpath(
            "/modeling/structure[@name='finalpos']/crystal/varray[@name='basis']"
        )[0].xpath("string(.)")
        cellarray = np.array(basis.split(), dtype=float).reshape(3, 3)
        return cellarray

    @cached_property
    def rec_cell(self):
        basis = self.file.xpath(
            "/modeling/structure[@name='finalpos']/crystal/varray[@name='rec_basis']"
        )[0].xpath("string(.)")
        cellarray = np.array(basis.split(), dtype=float).reshape(3, 3)
        return cellarray

    @cached_property
    def fermi(self):
        fermi_energy = float(self.file.xpath("/modeling/calculation/dos/i")[0].text)
        return fermi_energy

    @cached_property
    def kpoints(self):
        kpoints = self.file.xpath("/modeling/kpoints/varray[@name='kpointlist']")[
            0
        ].xpath("string(.)")
        kpointsarray = np.array(kpoints.split(), dtype=float).reshape(-1, 3)
        return kpointsarray[self.k_index]

    @cached_property
    def weights(self) -> npt.NDArray[np.float64]:
        weights = self.file.xpath("/modeling/kpoints/varray[@name='weights']")[0].xpath(
            "string(.)"
        )
        weightsarray = np.array(weights.split(), dtype=float)
        return weightsarray

    @cached_property
    def nbands(self):
        nbands = int(
            self.file.xpath(
                "/modeling/parameters/separator[@name='electronic']/i[@name='NBANDS']"
            )[0].text
        )
        return nbands

    @cached_property
    def total_dos(self):
        """A three-dimensional array about density of states

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first dimension represents the different spins

            The second demension represents the different points of energy

            The third demension has three columns and they represent energy, total and integrated respectively.

        """
        dos = self.file.xpath("/modeling/calculation/dos/total/array/set")[0].xpath(
            "string(.)"
        )
        dosarray = np.array(dos.split(), dtype=float).reshape(-1, self.nedos, 3)
        return dosarray

    @cached_property
    def dose(self) -> npt.NDArray[np.float64]:
        dose = self.total_dos[:, :, 0]
        return dose[0]

    @cached_property
    def dos(self):
        dos = self.total_dos[:, :, 1]
        return dos

    @cached_property
    def dosi(self):
        dosi = self.total_dos[:, :, 2]
        return dosi

    @cached_property
    def dospar(self):
        dospar = self.partial_dos[:, :, :, 1:].transpose(1, 0, 3, 2)
        return dospar

    @cached_property
    def partial_dos(self):
        """A four-dimensional array about partial dos

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first dimension represents the different ions

            The second demension represents the different spins

            The third demension represents the different points of energy, the totol is nedos

            The fourth demension represents the energy and different orbitals, the index 0 is energy and orbitals start index from 1
        """
        dos = self.file.xpath("/modeling/calculation/dos/partial/array/set")[0].xpath(
            "string(.)"
        )
        orbitals = self.file.xpath("/modeling/calculation/dos/partial/array/field")
        dosarray = np.array(dos.split(), dtype=float).reshape(
            self.ionnum, -1, self.nedos, len(orbitals)
        )
        return dosarray

    @cached_property
    def eigenvalues(self):
        """A four-dimensional array about eigenvalues

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first dimension represents the different spins

            The second demension represents the different kpoints

            The third demension represents the different bands

            The fourth demension has two columns and they represent eigenenergy and occupied number respectively.
        """
        eigen = self.file.xpath("/modeling/calculation/eigenvalues/array/set")[0].xpath(
            "string(.)"
        )
        eigenarray = np.array(eigen.split(), dtype=float).reshape(
            -1, len(self.kpoints), self.nbands, 2
        )[:, :, :, 0]
        return eigenarray[:, self.k_index, :]

    @cached_property
    def orbital_num(self):
        return self.dospar.shape[2]

    @cached_property
    def projected(self):
        """A five-dimensional array about partial dos

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first dimension represents the different spins

            The second demension represents the different ions

            The third demension represents  different orbitals, the orbitals start index from 0

            The fourth demension represents the different kpoints

            The fifth demension represents the different bands
        """
        projectstring = self.file.xpath(
            "string(/modeling/calculation/projected/array/set)"
        )
        orbitals = self.file.xpath("/modeling/calculation/projected/array/field")
        projectarray = (
            np.fromstring(projectstring.__str__(), dtype=np.float64, sep=" ")
            .reshape(-1, len(self.kpoints), self.nbands, self.ionnum, len(orbitals))
            .transpose([0, 3, 4, 1, 2])
        )
        return projectarray[:, :, :, self.k_index, :]

    @cached_property
    def symbols_dict(self):
        symbol_dict = dict((key, []) for key in self.symbols)
        for index, symbol in enumerate(self.symbols):
            symbol_dict[symbol].append(index)
        return symbol_dict

    @cached_property
    def symbols_str(self):
        result = []
        for key, value in self.symbols_dict.items():
            index_list = [[value[0]]]
            index_str_list = []
            for v in value[1:]:
                if v - 1 not in value:
                    index_list.append([])
                    index_list[-1].append(v)
                else:
                    index_list[-1].append(v)
            for subindex in index_list:
                if len(subindex) == 1:
                    index_str_list.append(f"{subindex[0]}")
                else:
                    index_str_list.append(f"{subindex[0]}-{subindex[-1]}")

            result.append(f"{key}: " + "+".join(index_str_list))
        return result
