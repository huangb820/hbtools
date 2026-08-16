---
name: hbtools-dev
description: hbtools(VASP 计算工具包)项目开发工作流规范 —— CLI 命令结构约定、vp 谷极化等关键命令说明、测试方法、命名风格、中文提交与 GitHub 对比/推送流程。新增、修改 hbtools 命令或需要提交推送时使用。
---

# hbtools 开发工作流

对 `C:\all\sci_re\VScode\git\hbtools`(VASP 能带/态密度/输入文件/计算作业工具包)做开发、调试、提交时遵循本规范。

## 项目结构

```
src/hbtools/
├── __init__.py          # 顶层 typer app,子模块 app 在此 add_typer 注册
├── subfig.py
├── vasp/                # band/dos 绘图、dataread(h5/xml 读取)、vasp_utils
├── input/               # INCAR/POTCAR/KPOINTS 等输入文件生成
├── calc/                # 计算作业模板(Jinja2)与批量生成
├── wannier/             # Wannier90 相关(本地独有,未发布到上游 GitHub 的部分)
└── utils/               # cli_utils(dataclass_cli)、plot_utils、common_params
```

- 入口:pyproject `[project.scripts]` 定义 `hb = "hbtools:app"`、`hbi = "hbtools.input.cli:app"`。
- 顶层 app 在 `__init__.py`:`app.add_typer(vasp_app, name="vasp")` 等;`context_settings={"help_option_names": ["-h", "--help"]}`。

## CLI 约定

- 每个子模块有自己的 `cli.py`,`app = typer.Typer(no_args_is_help=True)`。
- **命令体懒加载**:在命令函数内 `from ... import`(见 `vasp/cli.py` 的 `band`/`dos`),配合 `cli_utils.py` 的 `should_define` 加速自动补全,勿在模块顶部全量导入重依赖。
- **dataclass_cli 模式**:参数多时定义 `@dataclass` 的 `Params` 类(如 `vasp/band/params.py`),命令写作
  ```python
  @app.command("band")
  @dataclass_cli
  def band(params: BandParams):
      ...
  ```
  实现见 `utils/cli_utils.py`(把 dataclass 字段展开为 CLI 选项)。
- **参数风格**:`Annotated[type, typer.Option("-x", "--xxx", help=...)]`;文件格式类参数用 `click_type=click.Choice(["h5","xml"])` 并带 `envvar="MXMF_VASPFILE_FORMAT"` 约定;文件参数用 `typer.Argument(exists=True)`。
- 返回 None 的打印型命令添加 `-> None` 注解并直接用 `rich.print`。

## 关键命令:`vp` 谷极化

`hb vasp vp [FILE]`,读取 `vaspout.h5`(或 `-vf xml` 读 `vasprun.xml`),计算价带顶(VBM)能带在两个谷 K 点(K+/K-)的能量差(谷极化)。

- **手动模式(默认)**:`-p1` / `-p2` 指定两个 Kreuzung 点索引(默认 49 / 149),可选 `-v "b1 b2"` 按自旋显式给 VBM 带号。
- **自动模式**:`-a/--auto` 通过 `_valley_kpoints` 找 VBM 带沿 k 路径能量最高的**两个局域极大值**作为谷点(平顶峰会折叠为单峰,k 路径端点可能计入),并打印选中索引,可据此切回手动模式复现。
- 金属性能带(能带跨越费米面)会提示"为金属,跳过",不输出数值。
- 底层在 `vasp/vasp_utils.py::get_valley_polarizations`,辅助函数 `_local_maxima_indices` / `_valley_kpoints`(纯 numpy,项目未依赖 scipy)。

## 测试

- **不要用 PATH 上的 `python`**:Windows 商店 stub(`WindowsApps\python.exe`)直接退出码 49。必须用仓库 venv `& "C:\all\sci_re\VScode\git\hbtools\.venv\Scripts\python.exe"`。
- 无 h5 测试数据,用合成 numpy 数组做逻辑验证;
- CLI 接线用 typer CliRunner(已验证过):
  ```python
  python -c "from hbtools import app; from typer.testing import CliRunner; r=CliRunner().invoke(app, ['vasp','vp','--help']); print(r.output); print('exit', r.exit_code)"
  ```
- 改动后跑 `python -m py_compile <改动文件>` 确认语法。

## 提交与推送

- 提交信息用**中文**,按主题拆分清晰提交(参考历史:`统一谷极化函数命名为复数…`、`vp 命令新增 --auto…`)。
- 仓库有大量**未跟踪的带后处理脚本/输出目录**(1.py、2/、paper_output*/、scripts/ 等),提交时只 `git add` 本次相关的路径,**不要** `git add -A` 把无关文件带进去。
- `git commit` 可能触发 git 自动 housekeeping 长时间卡住(曾有 120s 超时后实际已提交成功),重试前先 `git log` 确认。
- 推送:`git push origin main`,远程为 `git@github.com:huangb820/hbtools.git`(SSH)。
- 与上游对比:本地通常是领先 GitHub 的版本(如 wannier 模块、`--auto` 功能仅本地有);对比用 `git fetch origin` + `git diff origin/main` 或按文件 `$(Get-FileHash)` 逐一对齐。