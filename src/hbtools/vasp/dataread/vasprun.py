from functools import cached_property
from typing import cast
from .vaspdata import VaspData
import numpy as np
from pathlib import Path
from lxml.etree import parse, ElementBase
import numpy.typing as npt


class ReadVasprun(VaspData):
    def __init__(
        self, file: str | Path = Path("vasprun.xml"), auto_select_k: bool = False
    ):
        self.file = parse(file)
        if auto_select_k:
            self.k_index = np.where(self.weights == 0)[0]
            if list(self.k_index) == []:
                print("here")
                self.k_index = np.where(self.weights > 0)[0]
        else:
            self.k_index = np.where(self.weights > 0)[0]

    def _get_data_str(self, xpath: str) -> str:
        data = cast(str | None, self.file.xpath(f"string({xpath})"))
        if data is None:
            raise ValueError(f"can't get data by {xpath}")
        else:
            return data

    def _symbols(self) -> list[str]:
        symbolstr = self._get_data_str("/modeling/atominfo/array[@name='atoms']/set[1]")
        return symbolstr.split()[0:-1:2]

    def _ionnum(self) -> int:
        return int(self._get_data_str("/modeling/atominfo/atoms"))

    def _positions(self) -> npt.NDArray[np.floating]:
        position_str = self._get_data_str(
            "/modeling/structure[@name='finalpos']/varray[@name='positions']"
        )
        return np.array(position_str.split(), dtype=float).reshape(-1, 3)

    def _real_cell(self) -> npt.NDArray[np.floating]:
        basis_str = self._get_data_str(
            "/modeling/structure[@name='finalpos']/crystal/varray[@name='basis']"
        )
        return np.array(basis_str.split(), dtype=float).reshape(3, 3)

    # kpoints
    def _kpoints(self) -> npt.NDArray[np.floating]:
        kpoints_str = self._get_data_str("/modeling/kpoints/varray[@name='kpointlist']")
        kpointsarray = np.array(kpoints_str.split(), dtype=float).reshape(-1, 3)
        return kpointsarray[self.k_index]

    def _weights(self) -> npt.NDArray[np.floating]:
        weights_str = self._get_data_str("/modeling/kpoints/varray[@name='weights']")
        return np.array(weights_str.split(), dtype=float)

    def _labels_kpoints(self) -> list[str] | None:
        return None

    def _kpoints_division(self) -> int | None:
        return None

    def _fermi(self) -> float:
        return float(self._get_data_str("/modeling/calculation/dos/i"))

    def _nbands(self) -> int:
        return int(
            self._get_data_str(
                "/modeling/parameters/separator[@name='electronic']/i[@name='NBANDS']"
            )
        )

    def _eigenvalues(self) -> npt.NDArray[np.floating]:
        eigen_str = self._get_data_str("/modeling/calculation/eigenvalues/array/set")
        eigenarray = np.array(eigen_str.split(), dtype=float).reshape(
            -1, len(self.kpoints), self.nbands, 2
        )[:, :, :, 0]
        return eigenarray[:, self.k_index, :]

    def _projected(self) -> npt.NDArray[np.floating]:
        project_str = self._get_data_str("/modeling/calculation/projected/array/set")
        orbitals = cast(
            list[ElementBase], self.file.xpath("/modeling/calculation/projected/array")
        )
        orbital_num = len(orbitals)
        projectarray = (
            np.fromstring(project_str, dtype=np.float64, sep=" ")
            .reshape(-1, len(self.kpoints), self.nbands, self.ionnum, orbital_num)
            .transpose([0, 3, 4, 1, 2])
        )
        return projectarray[:, :, :, self.k_index, :]

    # dos

    @cached_property
    def _tdos(self) -> npt.NDArray[np.floating]:
        dos_str = self._get_data_str("/modeling/calculation/dos/total/array/set")
        dosarray = np.array(dos_str.split(), dtype=float).reshape(-1, self.nedos, 3)
        return dosarray

    def _dose(self) -> npt.NDArray[np.floating]:
        return self._tdos[:, :, 0]

    def _dos(self) -> npt.NDArray[np.floating]:
        return self._tdos[:, :, 1]

    def _dosi(self) -> npt.NDArray[np.floating]:
        return self._tdos[:, :, 2]

    def _dospar(self) -> npt.NDArray[np.floating]:
        orbitals = cast(
            list[ElementBase],
            self.file.xpath("/modeling/calculation/dos/partial/array/field"),
        )
        orbital_num = len(orbitals)
        dos_str = self._get_data_str("/modeling/calculation/dos/partial/array/set")
        dosarray = np.array(dos_str.split(), dtype=float).reshape(
            self.ionnum, -1, self.nedos, orbital_num
        )
        return dosarray[:, :, :, 1:].transpose(1, 0, 3, 2)

    def _nedos(self) -> int:
        return int(
            self._get_data_str(
                "/modeling/parameters/separator[@name='dos']/i[@name='NEDOS']"
            )
        )
