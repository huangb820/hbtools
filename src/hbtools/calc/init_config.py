from pathlib import Path
import typer
import rtoml
from rich.console import Console

console = Console()
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "calc_params.toml"


def init_config(main_file:Path= CONFIG_DIR):
    """
    初始化配置文件
    """
    main_file.parent.mkdir(parents=True, exist_ok=True)
    config_path = main_file / CONFIG_FILE

    # 如果配置文件已存在，询问是否覆盖
    if config_path.exists():
        overwrite = typer.confirm(
            f"配置文件 {config_path} 已存在，是否覆盖？",
            default=False
        )
        if not overwrite:
            typer.echo("保留原有配置文件，退出初始化。")
            return

    # 初始化 INCAR 参数
    incar_params: dict[str, int | tuple[int, int, int] | float | str | bool] = {"encut": 600,
                "kpts": (12, 12, 1),
                "ediff": 1e-6,
                "ediffg": -0.01,
                "prec": "Accurate",
                "algo": "normal",
                "xc": "PBE",
                "ibrion": -1,
                "icharg": 2,
                "isif": 2,
                "istart": 0,
                "nelm": 300,
                "nsw": 0,
                "setups": "recommended",
                "gamma": True,
                "lorbit": 11,
                'lreal':False,
                'lwave':False,
                'lcharg':False,
                'ncore':4,
                'lmaxmix':4,
                'gga_compat':False,
                "ismear": 0,
                'sigma':0.05}
    # U值参数
    U_params: dict[str, dict[str, float | int]] = {
    "default": {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    # ===== 3d 过渡金属 =====
    "Sc": {"LDAUU": 2.9, "LDAUJ": 0.7, "LDAUL": 2},
    "Ti": {"LDAUU": 4.4, "LDAUJ": 0.7, "LDAUL": 2},
    "V":  {"LDAUU": 2.7, "LDAUJ": 0.7, "LDAUL": 2},
    "Cr": {"LDAUU": 3.5, "LDAUJ": 0.7, "LDAUL": 2},
    "Mn": {"LDAUU": 4.0, "LDAUJ": 0.7, "LDAUL": 2},
    "Fe": {"LDAUU": 4.6, "LDAUJ": 1.0, "LDAUL": 2},
    "Co": {"LDAUU": 5.0, "LDAUJ": 1.0, "LDAUL": 2},
    "Ni": {"LDAUU": 5.1, "LDAUJ": 1.0, "LDAUL": 2},
    "Cu": {"LDAUU": 4.0, "LDAUJ": 1.0, "LDAUL": 2},
    "Zn": {"LDAUU": 7.5, "LDAUJ": 1.0, "LDAUL": 2},
    # ===== 4d 过渡金属 =====
    "Y":  {"LDAUU": 4.3, "LDAUJ": 0.8, "LDAUL": 2},
    "Zr": {"LDAUU": 4.2, "LDAUJ": 0.8, "LDAUL": 2},
    "Nb": {"LDAUU": 2.1, "LDAUJ": 0.8, "LDAUL": 2},
    "Mo": {"LDAUU": 2.4, "LDAUJ": 0.8, "LDAUL": 2},
    "Tc": {"LDAUU": 2.7, "LDAUJ": 0.8, "LDAUL": 2},
    "Ru": {"LDAUU": 3.0, "LDAUJ": 0.8, "LDAUL": 2},
    "Rh": {"LDAUU": 3.3, "LDAUJ": 0.8, "LDAUL": 2},
    "Pd": {"LDAUU": 3.6, "LDAUJ": 0.8, "LDAUL": 2},
    "Ag": {"LDAUU": 5.8, "LDAUJ": 1.0, "LDAUL": 2},
    "Cd": {"LDAUU": 2.1, "LDAUJ": 0.8, "LDAUL": 2},
    # ===== 5d 过渡金属 =====
    "Hf": {"LDAUU": 3.5, "LDAUJ": 0.9, "LDAUL": 2},
    "Ta": {"LDAUU": 2.0, "LDAUJ": 0.9, "LDAUL": 2},
    "W":  {"LDAUU": 2.2, "LDAUJ": 0.9, "LDAUL": 2},
    "Re": {"LDAUU": 2.4, "LDAUJ": 0.9, "LDAUL": 2},
    "Os": {"LDAUU": 2.6, "LDAUJ": 0.9, "LDAUL": 2},
    "Ir": {"LDAUU": 2.8, "LDAUJ": 0.9, "LDAUL": 2},
    "Pt": {"LDAUU": 3.0, "LDAUJ": 0.9, "LDAUL": 2},
    "Au": {"LDAUU": 4.0, "LDAUJ": 1.0, "LDAUL": 2},
    "Hg": {"LDAUU": 2.1, "LDAUJ": 0.9, "LDAUL": 2},
    # ===== 镧系 + 锕系（f 轨道）=====
    "La": {"LDAUU": 8.1, "LDAUJ": 0.6, "LDAUL": 3},
    "Ce": {"LDAUU": 7.0, "LDAUJ": 0.7, "LDAUL": 3},
    "Pr": {"LDAUU": 6.5, "LDAUJ": 1.0, "LDAUL": 3},
    "Nd": {"LDAUU": 7.2, "LDAUJ": 1.0, "LDAUL": 3},
    "Sm": {"LDAUU": 7.4, "LDAUJ": 1.0, "LDAUL": 3},
    "Eu": {"LDAUU": 6.4, "LDAUJ": 1.0, "LDAUL": 3},
    "Gd": {"LDAUU": 6.7, "LDAUJ": 0.1, "LDAUL": 3},
    "Tb": {"LDAUU": 7.0, "LDAUJ": 1.0, "LDAUL": 3},
    "Dy": {"LDAUU": 6.8, "LDAUJ": 1.0, "LDAUL": 3},
    "Ho": {"LDAUU": 7.1, "LDAUJ": 1.0, "LDAUL": 3},
    "Er": {"LDAUU": 7.2, "LDAUJ": 1.0, "LDAUL": 3},
    "Tm": {"LDAUU": 7.3, "LDAUJ": 1.0, "LDAUL": 3},
    "Yb": {"LDAUU": 7.4, "LDAUJ": 1.0, "LDAUL": 3},
    "Lu": {"LDAUU": 4.8, "LDAUJ": 0.8, "LDAUL": 3},
    "Th": {"LDAUU": 5.0, "LDAUJ": 0.0, "LDAUL": 3},
    "U":  {"LDAUU": 4.0, "LDAUJ": 0.0, "LDAUL": 3},
    # ===== 非金属默认不加U =====
    "O":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "N":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "C":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "F":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "S":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "P":  {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},
    "Cl": {"LDAUU": 0.0, "LDAUJ": 0.0, "LDAUL": -1},}

    # 合并配置
    calc_dict = {
        "incar_params": incar_params,
        "U_params": U_params
    }

    with open(config_path, "w") as file:
        rtoml.dump(calc_dict, file)

    typer.echo(f"配置文件已创建: {config_path}")