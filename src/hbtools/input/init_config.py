from pathlib import Path
import typer
import rtoml
from rich.console import Console

console = Console()
CONFIG_DIR = Path.home() / ".config" / "hbtools"
CONFIG_FILE = CONFIG_DIR / "vasp_input.toml"


def init_config(main_file:Path= CONFIG_DIR):
    """
    初始化 VASP 输入配置文件，设置 PBE/GGA/LDA 三类 POTCAR 赝势路径。
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
        rtoml.dump(input_dict, file)

    typer.echo(f"配置文件已创建: {config_path}")