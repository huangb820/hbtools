# hbtools

针对 VASP 计算的一站式命令行工具包:读取能带/态密度数据并出图、计算带隙与谷极化、生成输入文件、批量生成计算作业,并支持 Wannier90 相关操作。

- 基于 `typer` 的命令行,`-h`/`--help` 可查看每个命令的完整选项
- 原生支持 `vaspout.h5`(VASP 6)与 `vasprun.xml` 两种格式
- 提供了共享的 `matplotlibrc` 绘图风格与统一的图形/配色参数

## 功能特性

| 模块 | 命令 | 说明 |
|---|---|---|
| `vasp` | `band` | 画能带图,支持投影(轨道/原子)、自旋、`vaspout.h5`/`vasprun.xml` |
| | `dos` | 画态密度(DOS)图,支持投影、总 DOS、色带 |
| | `gap` | 计算带隙,可指定价带顶带号 |
| | `vp` | 计算**谷极化**(两个谷 K 点处的能带能量差) |
| | `nbands_ewin` | 统计给定能量窗口内的能带数 |
| `input` | `init`/`kpoints`/`potcar` | 生成输入文件 |
| `calc` | — | 通过 Jinja2 模板批量生成计算作业 |
| `wannier` | `incar` | Wannier90 相关操作 |

所有子命令统一挂在 `hb` 下:

```
hb subfig | vasp | input | calc | wannier
      └─ vasp: band | dos | gap | vp | nbands_ewin
      └─ input: init | kpoints | potcar
      └─ wannier: incar
```

输入文件格式通过环境变量约定:`MXMF_VASPFILE_FORMAT`(`h5`/`xml`),绘图风格文件路径为 `MXMF_MATPLOTLIBRC`(默认 `~/.config/mxmftools/…`)。

## 安装

需要 Python ≥ 3.11,推荐使用 [`uv`](https://docs.astral.sh/uv/)。

**作为库安装进项目**

```bash
uv init
uv add hbtools@git+https://github.com/huangb820/hbtools.git
```

**全局安装为命令行工具**

```bash
uv tool install hbtools@git+https://github.com/huangb820/hbtools.git
```

这样即可直接使用 `hb`(主命令)与 `hbi`(输入文件命令)两个可执行文件。

## 快速上手

所有 `vasp` 子命令默认读取当前目录下的 `vaspout.h5`;若用 XML 结果,加 `-vf xml` 指向 `vasprun.xml`。

**画能带图**

```bash
# 读取 vaspout.h5,设费米能为 -2.5 eV,红/蓝两条线,导出 band.png(默认)
hb vasp band vaspout.h5 -ef -2.5 -c "red blue"

# 轨道投影能带(从 vasprun.xml 读取,投影模式 pmode=1)
hb vasp band vasprun.xml -vf xml -p "1-d;2-p" -pm 1 --save band_proj.svg
```

**画态密度图**

```bash
hb vasp dos vaspout.h5 -ef -2.5 -pm 2 --save dos.png
```

**计算带隙**

```bash
hb vasp gap vaspout.h5
# 若自动判定的价带顶带号不准,可用 -v 显式指定各自旋的带号,如:
hb vasp gap vaspout.h5 -v "6 6"
```

**计算谷极化**

```bash
# 手动指定两个谷 K 点(默认 K+=49,K-=149)
hb vasp vp vaspout.h5 -p1 49 -p2 149

# 自动:按价带顶能带的局域极大值自动选取两个能量最高的谷点
hb vasp vp vaspout.h5 --auto
```

`--auto` 会打印自动选中的谷点索引与能量,方便核对后再切回手动模式精确复现。

**统计能量窗口内的能带数**

```bash
hb vasp nbands_ewin vaspout.h5 -ew -2 2
```

**生成输入文件**

```bash
hb input init
hb input kpoints
hb input potcar
```

## 依赖

完整依赖见 `pyproject.toml`。核心包括:`h5py`(读取 vaspout.h5)、`lxml`(解析 XML)、`matplotlib` + `numpy`(绘图/数值)、`typer` + `rich`(命令行/输出)、`jinja2`(计算作业模板)、`seekpath`/`spinmc`/`ase-abacus` 等。其中 `numpy`/`contourpy` 的版本上限为兼容 CentOS 7。

## 开发

```bash
# 使用仓库自带的虚拟环境
.venv\Scripts\python.exe -m py_compile src\hbtools\vasp\cli.py
```

开发约定(CLI 结构、`dataclass_cli` 用法、测试方法与提交规范)详见仓库内 `.claude/skills/hbtools-dev`。

## License

[MIT](LICENSE)