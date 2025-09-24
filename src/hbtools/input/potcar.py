import json
from pathlib import Path
from ase import Atoms
from ase.io import read
from .params import POTCARParams
from rich.console import Console
from rich.table import Table
import typer
import rtoml


console = Console()
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "vasp_input.toml"


def get_pseudo_dir(key: str) -> str:
    if not CONFIG_DIR.exists():
        typer.echo("配置文件不存在，请先运行 'hbtools input init' 初始化配置。")
        return ""
    with open(CONFIG_FILE, "r") as file:
        toml_data: dict[str, dict[str, str]] = rtoml.load(file)

    pseudo_dir: dict[str, str] | None = toml_data.get("pseudo_dir")
    if pseudo_dir is None:
        typer.echo("未找到 POTCAR 赝势目录，请重新运行 'hbtools input init' 初始化配置。")
        return ""
    pseudo_path = pseudo_dir.get(key)
    if pseudo_path is None:
        typer.echo(f"未找到 {key} 类型的 POTCAR 赝势路径，请重新运行 'hbtools input init' 初始化配置。")
        return ""
    return pseudo_path

def get_elements(params: POTCARParams) -> list[str]:
    """
    获取元素顺序：
    1. 如果用户指定 --select-elements，则直接解析
    2. 否则读取 POSCAR 中的元素
    """
    if params.select_elements:
        elements = params.select_elements.split()
    else:
        poscar_path = params.work_dir / params.input_filename
        if not poscar_path.exists():
            raise FileNotFoundError(f"POSCAR 文件不存在: {poscar_path}")
        atoms = read(poscar_path)
        if isinstance(atoms, list):
            atoms = atoms[0]
        elements = list(dict.fromkeys(atoms.get_chemical_symbols()))  # 保持顺序去重

    return elements

"""
with open(poscar_path, "r") as file:
        lines = file.readlines()
        # 提取元素信息
        elements = []
        for line in lines[5:]:
            elements.extend(line.split())
        return elements
"""

def write_potcar(params: POTCARParams):
    """
    根据输入参数生成POTCAR文件内容
    """
    pseudo_base: str = get_pseudo_dir(params.pseudo_type)
    elements: list[str]= get_elements(params)
    potcar_content = ""

    table = Table(title="POTCAR 信息", show_header=True, header_style="bold magenta")
    table.add_column("元素", justify="center")
    table.add_column("POTCAR 路径", justify="left")

    for elem in elements:
        elem_dir = Path(pseudo_base) / elem
        potcar_path = elem_dir / "POTCAR"
        if not potcar_path.exists():
            raise FileNotFoundError(f"{elem} 的 POTCAR 文件不存在: {potcar_path}")
        with open(potcar_path, "r") as f:
            potcar_content += f.read().strip() + "\n"
        table.add_row(elem, str(potcar_path))

    console.print(table)

    potcar_str = potcar_content
    output_path = params.work_dir / params.output_filename
    with open(output_path, "w") as f:
        f.write(potcar_str)
    console.print(f"[bold green]POTCAR 文件已生成: {output_path}[/]")


