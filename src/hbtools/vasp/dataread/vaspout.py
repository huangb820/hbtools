from .vaspdata import VaspData

from pathlib import Path

import h5py  # pyright: ignore[reportMissingTypeStubs]
import numpy as np
import numpy.typing as npt


class ReadVaspout(VaspData):
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
        # super().__init__()

    # structure

    def _symbols(self) -> list[str]:
        ion_types = np.array(self.file.get("results/positions/ion_types"))  # type: ignore
        number_ion_types = np.array(self.file.get("results/positions/number_ion_types")) # type: ignore
        symbols: list[str] = []
        for i, ion in enumerate(ion_types):
            symbols.extend([ion.decode("utf-8")] * number_ion_types[i])
        return symbols

    def _ionnum(self) -> int:
        return int(np.array(self.file.get("results/positions/number_ion_types")).sum())

    def _positions(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/positions/position_ions"))

    def _real_cell(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/positions/lattice_vectors"))

    # kpoints
    def _kpoints(self) -> npt.NDArray[np.floating]:
        return np.array(
            self.file.get(f"results/electron_eigenvalues{self.prefix2}/kpoint_coords")
        )

    def _weights(self) -> npt.NDArray[np.floating]:
        return np.array(
            self.file.get(
                f"results/electron_eigenvalues{self.prefix2}/kpoints_symmetry_weight"
            )
        )

    def _labels_kpoints(self) -> list[str] | None:
        labels = self.file.get(f"input/kpoints{self.prefix1}/labels_kpoints")  # pyright: ignore[reportUnknownVariableType]
        if labels is None:
            return None

        labels_array = np.array(labels)
        xticklabels = [i.decode("utf8") for i in labels_array]
        return xticklabels

    def _kpoints_division(self) -> int | None:
        mode = self.file.get(f"input/kpoints{self.prefix1}/mode")  # pyright: ignore[reportUnknownVariableType]
        if np.array(mode) == b"l":
            return int(
                np.array(self.file.get(f"input/kpoints{self.prefix1}/number_kpoints"))
            )
        return None

    def _fermi(self) -> float:
        return float(np.array(self.file.get("results/electron_dos/efermi")))

    def _nbands(self) -> int:
        return self.eigenvalues.shape[-1]

    def _eigenvalues(self) -> npt.NDArray[np.floating]:
        eigenvalues = np.array(
            self.file.get(f"results/electron_eigenvalues{self.prefix2}/eigenvalues")
        )
        return eigenvalues[:, self.k_index, :]

    def _projected(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get(f"results/projectors{self.prefix2}/par"))[
            :, :, :, self.k_index, :
        ]

    # dos
    def _dos(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/electron_dos/dos"))

    def _dose(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/electron_dos/energies"))

    def _dosi(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/electron_dos/dosi"))

    def _dospar(self) -> npt.NDArray[np.floating]:
        return np.array(self.file.get("results/electron_dos/dospar"))

    def _nedos(self) -> int:
        return int(np.array(self.file.get("results/electron_dos/nedos")))
