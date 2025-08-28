from typing import Annotated
import typer
from pathlib import Path


app = typer.Typer(no_args_is_help=True)


@app.command("subfig")
def subfig(
    out_file=Path("subfig.py"),
    rows: Annotated[int, typer.Argument()] = 2,
    cols: Annotated[int, typer.Argument()] = 2,
    marker: Annotated[bool, typer.Option()] = False,
    rit: Annotated[bool, typer.Option] = False,
):
    import itertools
    import inspect

    with open(out_file, "w") as fo:
        share = ", sharex=True, sharey=True" if rit else ""
        fo.write(
            inspect.cleandoc(
                f"""
                import matplotlib.pyplot as plt


                from hbtools.utils.plot_utils import plot_from_cli_str

                fig, axs = plt.subplots(nrows={rows}, ncols={cols} {share})
                axs = axs.flat
                """
            )
            + "\n"
        )
        fo.write("\n")

        fo.write(
            "fig.set_constrained_layout_pads(w_pad=0.04167, h_pad=0.04167, hspace=0.02, wspace=0.02)\n"
        )
        fo.write("\n")

        for i, j in itertools.product(range(rows), range(cols)):
            fo.write(f'plot{i + 1}{j + 1}_args=  "plot band vaspout.h5 -yr -2 2"\n')
        fo.write("\n")

        for i, j in itertools.product(range(rows), range(cols)):
            fo.write(
                f"plot{i + 1}{j + 1} =  plot_from_cli_str(plot{i + 1}{j + 1}_args, fig=fig, ax=axs[{i * cols + j}])\n"
            )
        fo.write("\n")

        if marker:
            for i in range(rows * cols):
                fo.write(
                    f"axs[{i}].text(-0.2, 1, '({chr(i + 97)})', transform=axs[{i}].transAxes)\n"
                )
            fo.write("\n")
        if rit:
            fo.write("for ax in axs:\n    ax.label_outer(remove_inner_ticks=True)\n")

        fo.write("plt.show()\n")
