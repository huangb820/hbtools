from typing import List
from ase import Atoms
from ase.data import atomic_numbers, ground_state_magnetic_moments
from ase.io import read
from pathlib import Path
from collections import Counter
import rtoml

# 配置文件路径
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "calc_params.toml"

def load_config():
    """加载 TOML 配置文件"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在，请先运行 init_config: {CONFIG_FILE}")
    return rtoml.load(CONFIG_FILE)

def estimate_initial_magmoms(poscar_path: str = "POSCAR") -> list[float]:
    """
    根据 POSCAR 文件中的元素成分，结合 ASE 数据库和非金属零磁矩假设，
    计算初始磁矩设置 (MAGMOM)，用于 VASP INCAR。
    参数:
        poscar_path (str): POSCAR 文件路径。
    返回:
        list[float]: 每个原子的初始磁矩，按 POSCAR 顺序排列。
    """

    # 常见非金属元素列表（包括氢、卤素、O/N/C 等）
    NON_METALS = {
        "H", "He",
        "B", "C", "N", "O", "F", "Ne",
        "Si", "P", "S", "Cl", "Ar",
        "Ga", "Ge", "As", "Se", "Br", "Kr",
        "In", "Sn", "Sb", "Te", "I", "Xe",
        "Tl", "Pb", "Bi", "At", "Rn"
    }
    # 读取 POSCAR 结构
    atoms: Atoms | List[Atoms] = read(poscar_path, format="vasp")
    symbols = atoms.get_chemical_symbols()

    magmom_list: list[float] = []
    for sym in symbols:
        Z = atomic_numbers[sym]  # 原子序号

        # 非金属或稀有气体 → 磁矩设为 0
        if sym in NON_METALS:
            magmom = 0.0
        else:
            # 金属 → 从 ASE 数据库读取基态磁矩
            raw_magmom = ground_state_magnetic_moments[Z]
            magmom = float(raw_magmom) if raw_magmom is not None else 0.0

        magmom_list.append(magmom)

    return magmom_list

def get_ldau_from_poscar(poscar_path="POSCAR"):
    """根据 POSCAR 读取元素并生成 LDAU 参数"""
    config = load_config()
    u_params = config.get("U_params", {})
    atoms = read(poscar_path, format="vasp")
    symbols = atoms.get_chemical_symbols()
    comp = Counter(symbols)

    ldaul, ldauu, ldauj = [], [], []
    # 需要处理元素种类
    for sym in comp:
        # 获取该元素的 U 参数
        data = u_params.get(sym, u_params["default"])
        ldaul.append(str(data["LDAUL"]))
        ldauu.append(f"{data['LDAUU']:.2f}")
        ldauj.append(f"{data['LDAUJ']:.2f}")

    return list(comp.keys()), ldaul, ldauu, ldauj


from __future__ import annotations
import sys
from pathlib import Path
import toml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ase.io import read, ASEError
from typing import Optional, List, Dict
from ase.data import atomic_numbers,ground_state_magnetic_moments
from pymatgen.core.periodic_table import Element



# === 路径设置 ===
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "calc_params.toml"


def load_config():
    """加载全局配置文件，如果不存在则报错。"""
    if not CONFIG_FILE.exists():
        sys.exit(f"错误: 配置文件 {CONFIG_FILE} 不存在，请先运行 `hb init-config` 初始化。")
    return toml.load(CONFIG_FILE)

def get_ldau_luj(poscar_file: Path, config: dict) -> Dict[str, dict]:
    """根据 POSCAR 获取 U/J/L 参数。"""
    try:
        atoms = read(poscar_file)
    except (FileNotFoundError, ASEError):
        sys.exit(f"错误: 无法读取 {poscar_file}，请检查 POSCAR 文件格式。")

    u_values = config.get("U_params", {})
    luj = {}
    for symbol in set(atoms.get_chemical_symbols()):
        luj[symbol] = u_values.get(symbol, u_values.get("default", {}))
    return luj

def get_magmom_list(poscar_file: Path) -> List[float]:
    """根据 POSCAR 文件返回磁矩列表。"""
    try:
        atoms = read(poscar_file)
    except (FileNotFoundError, ASEError):
        sys.exit(f"错误: 无法读取 {poscar_file}，请检查 POSCAR 文件格式。")
    return [ground_state_magnetic_moments[atomic_numbers[sym]] for sym in atoms.get_chemical_symbols()]