import json
from pathlib import Path
from ase import Atoms
from ase.io import read
from .params import POTCARParams
from rich.console import Console
from rich.table import Table
import typer

console = Console()
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "vasp_input.json"

def init_config(main_file:Path= CONFIG_DIR):
    """
    初始化 VASP 输入配置文件，设置 PBE/GGA/LDA 三类 POTCAR 赝势路径。
    """
    main_file.parent.mkdir(parents=True, exist_ok=True)
    config_path = main_file / "vasp_input.json"

    # 如果配置文件已存在，询问是否覆盖
    if config_path.exists():
        overwrite = typer.confirm(
            f"配置文件 {config_path} 已存在，是否覆盖？",
            default=False
        )
        if not overwrite:
            typer.echo("保留原有配置文件，退出初始化。")
            return

    # 交互式输入赝势路径
    pseudo_pbe_dir = typer.prompt(
        "请输入 PBE 赝势路径",
        default="/path/to/vasp_opt/pot54/potpaw_PBE"
    )
    pseudo_gga_dir = typer.prompt(
        "请输入 GGA 赝势路径",
        default="/path/to/vasp_opt/pot54/potpaw_GGA"
    )
    pseudo_lda_dir = typer.prompt(
        "请输入 LDA 赝势路径",
        default="/path/to/vasp_opt/pot54/potpaw_LDA"
    )

    # 预设 INCAR 参数
    incar_presets = {
        "example1": {
            "ENCUT": 500,
            "kpt": (12, 12, 1)
        },
        "example2": {
            "ENCUT": 600,
            "kpt": (18, 18, 1)
        }
    }

    # 合并配置
    input_dict = {
        "pseudo_dir": {
            "PBE": pseudo_pbe_dir,
            "GGA": pseudo_gga_dir,
            "LDA": pseudo_lda_dir
        },
        "incar_params": incar_presets
    }

    with open(config_path, "w") as file:
        json.dump(input_dict, file, indent=4)

    typer.echo(f"配置文件已创建: {config_path}")


def get_pseudo_dir(key: str) -> str:
    if not CONFIG_DIR.exists():
        typer.echo("配置文件不存在，请先运行 'hbtools input init' 初始化配置。")
        return ""
    with open(CONFIG_FILE, "r") as file:
        json_data = json.load(file)
    pseudo_dir = json_data.get("pseudo_dir")
    pseudo_path = pseudo_dir.get(key)
    if not pseudo_path:
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


