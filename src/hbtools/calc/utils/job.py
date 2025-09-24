# hbtools/utils.py
import importlib.util
from pathlib import Path

def get_package_dir(package_name: str = "hbtools") -> str:
    """
    获取 hbtools 包的安装路径。
    默认返回 hbtools 的安装目录，支持传入其他包名。
    """
    spec = importlib.util.find_spec(package_name)
    if spec is None or spec.origin is None:
        raise ModuleNotFoundError(f"未找到包：{package_name}")
    return str(Path(spec.origin).parent)
