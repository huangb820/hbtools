from ase.io import read,write
from ase.calculators.vasp.create_input import (GenerateVaspInput,list_float_keys,list_int_keys)
import subprocess
import os
from ase import Atoms
from pathlib import Path
import shutil
from typing import Any

def vasp_input(atoms: Atoms, calc_params: dict[str, Any], calcdir: Path):
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

def vasprun(PREFIX: str, directory: str | os.PathLike[str]):
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

def relax(atoms:Atoms, work_dir:Path,PREFIX:str, calc_para : dict[str, Any], calc_file: str):
    relax_dir = work_dir / calc_file
    relax_para = {'nsw':100,'ibrion':2}
    calc_para = {**calc_para, **relax_para}
    vasp_input(atoms, calc_para, relax_dir)
    vasprun(PREFIX, relax_dir)
    relax_atoms = read(relax_dir / 'CONTCAR')
    return relax_atoms

def static(atoms:Atoms, work_dir:Path,PREFIX:str, calc_para : dict[str, Any], calc_file: str, pre_dir:str | None):
    static_dir = work_dir / calc_file
    static_para = {'istart':0,'icharg':2,'ismear':-5, 'lwave':True, 'lcharg':True}
    calc_para = {**calc_para, **static_para}
    vasp_input(atoms, calc_para, static_dir)
    if pre_dir is None:
        pass
    else:
        pre_file = work_dir / pre_dir
        for file in ['WAVECAR','CHGCAR','CHG']:
            shutil.copy( pre_file / file, static_dir / file)
        static_para['istart'] = 1
    vasprun(PREFIX, static_dir)
    print(f"**********   Successfully finished {calc_file} calculations   **********")

def wannier(atoms:Atoms, work_dir:Path, PREFIX:str, calc_para:dict[str, Any], calc_file:str, pre_dir:str|None):
    wannier_dir = work_dir / calc_file
    wannier_para = {'lreal':False,'lwave':False,'lcharg':False,'lmaxmix':4,'gga_compat':False}
    calc_para = {**calc_para, **wannier_para}
    vasp_input(atoms, calc_para, wannier_dir)
    if pre_dir is None:
        pass
    else:
        pre_file = work_dir / pre_dir
        for file in ['WAVECAR','CHGCAR','CHG']:
            shutil.copy( pre_file / file, wannier_dir / file)
    shutil.copy( './INCAR', wannier_dir / 'INCAR')
    vasprun(PREFIX, wannier_dir)
    print(f"**********   Successfully finished {calc_file} calculations   **********")

def kpoints_path(work_dir:Path, filename:str = 'KPOINTS'):
    fe = open( work_dir / filename,'w')
    fe.write('KPOINTS\n50\nLine-mode\nrec\n')
    fe.write('0.5 0.5 0.0   M\n0.5 0.0 0.0  X\n\n')
    fe.write('0.5 0.0 0.0   X\n0.0 0.0 0.0  G\n\n')
    fe.write('0.0 0.0 0.0   G\n0.0 0.5 0.0  Y\n\n')
    fe.write('0.0 0.5 0.0   Y\n0.5 0.5 0.0  M\n\n')
    fe.write('0.5 0.5 0.0   M\n0.0 0.0 0.0  G\n\n')
    fe.close()

def band(atoms:Atoms, work_dir:Path, PREFIX: str,calc_para : dict[str, Any], calc_file: str, pre_dir:str):
    band_dir = work_dir / calc_file
    band_para = {'istart':1,'icharg':11,'ismear':0, 'lwave':False, 'lcharg':False}
    calc_para = {**calc_para, **band_para}
    vasp_input(atoms, calc_para, band_dir)
    pre_file = work_dir / pre_dir
    for file in ['WAVECAR','CHGCAR','CHG']:
        shutil.copy( pre_file / file,band_dir / file)
    kpoints_path(band_dir)
    vasprun(PREFIX, band_dir)
    print(f"**********   Successfully finished {calc_file} calculations   **********")

