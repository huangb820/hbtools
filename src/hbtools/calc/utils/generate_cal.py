from __future__ import annotations
import sys
from pathlib import Path
import toml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ase.io import read
from typing import Optional, List, Dict

# === 路径设置 ===
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "calc_params.toml"
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_FILE = TEMPLATE_DIR / "band_calc.py.j2"

# === 默认磁矩估计 ===
MAGNETIC_CONFIG: Dict[str, float] = {
    "Fe": 4, "Co": 3, "Ni": 2, "Mn": 5,
    "Cr": 6, "V": 3, "Ti": 2, "O": 2
}

def estimate_magmom(symbol: str) -> float:
    """根据元素符号估算磁矩（μB）。"""
    return float(MAGNETIC_CONFIG.get(symbol, 0))

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
    return [estimate_magmom(sym) for sym in atoms.get_chemical_symbols()]

def generate_calc(
    poscar_file: Path = Path("POSCAR"),
    mag: bool = True,
    soc: bool = False,
    soc_conv: bool = False,
    wann: bool = False,
    strain_list: Optional[List[float]] = None,
    strain_mode: str = "biaxial",
    u_list: Optional[List[float]] = None,
    output: Path = Path("cal.py")
) -> None:
    """
    根据模板生成 VASP 计算脚本。
    """
    # 加载配置
    config = load_config()

    # 准备模板
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        template = env.get_template(TEMPLATE_FILE.name)
    except TemplateNotFound:
        sys.exit(f"错误: 找不到模板文件 {TEMPLATE_FILE}")

    # 获取参数
    defaults = config.get("incar_params", {})
    ldau_luj = get_ldau_luj(poscar_file, config)
    magmom_list = get_magmom_list(poscar_file)

    # 渲染模板
    rendered = template.render(-1
        original_para=defaults,
        ldau_luj=ldau_luj,
        poscar_file=str(poscar_file),
        mag=mag,
        soc=soc,
        soc_conv=soc_conv,
        wann=wann,
        strain_list=strain_list,
        strain_mode=strain_mode,
        u_list=u_list,
        magmom_list=magmom_list,
    )

    # 写入文件
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(rendered)

    print(f"✅ 成功生成计算脚本: {output}")

