from ase.io import read,write
from ase.calculators.vasp.create_input import (GenerateVaspInput,list_float_keys,list_int_keys)
import subprocess
import os
from ase import Atoms
from pathlib import Path



def vasp_input(atoms: Atoms, calc_params: dict, calcdir: Path):
    # add keys
    list_int_keys.append("ioptcell")
    list_float_keys.append("magmom")
    # make calculate directory
    calcdir.mkdir(parents=True, exist_ok=True) if not calcdir.exists() else ...
    # write poscar
    atoms.write(calcdir / "POSCAR")
    # write incar
    ase_input_gener = GenerateVaspInput()
    ase_input_gener.set(**calc_params)
    ase_input_gener.initialize(atoms)
    ase_input_gener.write_incar(atoms, str(calcdir))
    # write potcar
    ase_input_gener.write_potcar(directory=str(calcdir))
    # write kpoints
    ase_input_gener.write_kpoints(atoms, directory=str(calcdir))

def vasprun(PREFIX: str, directory: str | os.PathLike):
    command = os.getenv("ASE_VASP_COMMAND")
    if command is None:
        raise ValueError
    else:
        command = command.replace("PREFIX", PREFIX)
    with open(f"{directory}/vasp.out", "w") as outfile:
        errorcode = subprocess.run(
            command, shell=True, check=True, cwd=directory, stdout=outfile
        )
    print(errorcode)

# VASP input generation for ASE

def create_vasp_input(atoms: Atoms, calc_params: dict, calcdir: Path,):
    # add keys
    list_int_keys.append("ioptcell")
    list_float_keys.append("magmom")
    # make calculate directory
    calcdir.mkdir(parents=True, exist_ok=True) if not calcdir.exists() else ...
    ase_input_gener = GenerateVaspInput()
    ase_input_gener.set(**calc_params)
    ase_input_gener.initialize(atoms)
    return ase_input_gener

# INCAR
def incar_input(atoms: Atoms, calc_params: dict, calcdir: Path,):
    # make calculate directory
    calcdir.mkdir(parents=True, exist_ok=True) if not calcdir.exists() else ...
    # write incar
    ase_input_gener = create_vasp_input(atoms, calc_params, calcdir)
    ase_input_gener.write_incar(atoms, str(calcdir))

# KPOINTS
def kpoints_input(atoms: Atoms, calc_params: dict, calcdir: Path,):
    # make calculate directory
    calcdir.mkdir(parents=True, exist_ok=True) if not calcdir.exists() else ...
    # write kpoints
    ase_input_gener = create_vasp_input(atoms, calc_params, calcdir)
    ase_input_gener.write_kpoints(atoms, directory=str(calcdir))

# POTCAR
def potcar_input(atoms: Atoms, calc_params: dict, calcdir: Path,):
    # make calculate directory
    calcdir.mkdir(parents=True, exist_ok=True) if not calcdir.exists() else ...
    # write potcar
    ase_input_gener = create_vasp_input(atoms, calc_params, calcdir)
    ase_input_gener.write_potcar(directory=str(calcdir))