from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

import numpy as np
import numpy.typing as npt


class VaspData(ABC):
    def __init__(
        self,
        file: str | Path = "vaspout.h5",
        opt: bool | None = None,
        auto_select_k: bool = False,
    ):
        super().__init__()

    @abstractmethod
    def _symbols(self) -> list[str]: ...

    @abstractmethod
    def _ionnum(self) -> int: ...

    @abstractmethod
    def _positions(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _real_cell(self) -> npt.NDArray[np.floating]: ...

    # kpoints
    @abstractmethod
    def _kpoints(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _weights(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _labels_kpoints(self) -> list[str] | None: ...

    @abstractmethod
    def _kpoints_division(self) -> int | None: ...

    @abstractmethod
    def _fermi(self) -> float: ...

    @abstractmethod
    def _nbands(self) -> int: ...

    @abstractmethod
    def _eigenvalues(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _projected(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _dos(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _dose(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _dosi(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _dospar(self) -> npt.NDArray[np.floating]: ...

    @abstractmethod
    def _nedos(self) -> int: ...

    @cached_property
    def symbols(self) -> list[str]:
        return self._symbols()

    @cached_property
    def ionnum(self) -> int:
        return self._ionnum()

    @cached_property
    def positions(self) -> npt.NDArray[np.floating]:
        """Atomic positions in Cartesian coordinates.

        Returns
        -------
        numpy.ndarray, shape (ionnum, 3)
            Each row represents the (x, y, z) coordinates of an atom.
        """
        return self._positions()

    @cached_property
    def real_cell(self) -> npt.NDArray[np.floating]:
        """Real-space lattice vectors.

        Returns
        -------
        numpy.ndarray, shape (3, 3)
            Each row represents a lattice vector in Cartesian coordinates.
        """
        return self._real_cell()

    @cached_property
    def rec_cell(self) -> npt.NDArray[np.floating]:
        """Reciprocal lattice vectors.

        Returns
        -------
        numpy.ndarray, shape (3, 3)
            Each row represents a reciprocal lattice vector.
        """
        return np.linalg.inv(self.real_cell).T

    @cached_property
    def kpoints(self) -> npt.NDArray[np.floating]:
        """List of k-points in reciprocal space.

        Returns
        -------
        numpy.ndarray, shape (nkpoints, 3)
            k-point coordinates in reciprocal lattice units.
        """
        return self._kpoints()

    @cached_property
    def weights(self) -> npt.NDArray[np.floating]:
        """Weights of k-points for Brillouin zone integration.

        Returns
        -------
        numpy.ndarray, shape (nkpoints,)
            Weight of each k-point.
        """
        return self._weights()

    @cached_property
    def labels_kpoints(self) -> list[str] | None:
        return self._labels_kpoints()

    @cached_property
    def kpoints_division(self) -> int | None:
        return self._kpoints_division()

    @cached_property
    def fermi(self) -> float:
        return self._fermi()

    # band
    @cached_property
    def nbands(self) -> int:
        return self._nbands()

    @cached_property
    def eigenvalues(self) -> npt.NDArray[np.floating]:
        """A three-dimensional array about eigenvalues

        Returns:
        -------
        <class 'numpy.ndarray'>
            The first dimension represents the different spins

            The second demension represents the different kpoints

            The third demension represents the different bands
        """
        return self._eigenvalues()

    @cached_property
    def projected(self) -> npt.NDArray[np.floating]:
        """A five-dimensional array about projected band

        Returns:
        -------
        <class 'numpy.ndarray'>

            The first dimension represents the different spins

            The second demension represents the different ions

            The third demension represents  different orbitals

            The fourth demension represents the different kpoints

            The fifth demension represents the different bands
        """
        return self._projected()

    @cached_property
    def dose(self) -> npt.NDArray[np.floating]:
        """An 1-dimensional array of energy points for the system.

        Returns
        -------
        <class 'numpy.ndarray'>
            A one-dimensional array representing the energy points.
        """
        return self._dose()

    @cached_property
    def dos(self) -> npt.NDArray[np.floating]:
        """A two-dimensional array of density of states (DOS).

        Returns
        -------
        <class 'numpy.ndarray'>
            The first dimension represents different atoms or spin channels.

            The second dimension represents different energy points.
        """
        return self._dos()

    @cached_property
    def dosi(self) -> npt.NDArray[np.floating]:
        """A two-dimensional array of integrated density of states (IDOS).

        Returns
        -------
        <class 'numpy.ndarray'>
            The first dimension represents different atoms or spin channels.

            The second dimension represents different energy points.
        """
        return self._dosi()

    @cached_property
    def dospar(self) -> npt.NDArray[np.floating]:
        """A four-dimensional array of partial DOS (PDOS).

        Returns
        -------
        <class 'numpy.ndarray'>
            The first dimension represents different spins.

            The second dimension represents different atoms (ions).

            The third dimension represents different orbitals and energy channels.

            The fourth dimension represents the different energy points.
        """
        return self._dospar()

    @cached_property
    def nedos(self) -> int:
        return self._nedos()

    @cached_property
    def orbital_num(self) -> int:
        if "dospar" in self.__dict__:
            return self.dospar.shape[2]
        elif "projected" in self.__dict__:
            return self.projected.shape[2]
        else:
            return self.dospar.shape[2]
