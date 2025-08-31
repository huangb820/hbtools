import os
import dataclasses
import inspect
import sys
from typing import Any, Callable, Type, TypeVar, cast

"""
    
lazily defined all cli commands for Faster Auto-completion
Modified from https://github.com/fastapi/typer/issues/231#issuecomment-1312892589

"""


def should_define(command: str) -> bool:
    return _cli_is_invoking_command(
        command=command
    ) or _autocomplete_is_resolving_command(command=command)


def _cli_is_invoking_command(command: str) -> bool:
    return command in sys.argv


def _autocomplete_is_resolving_command(command: str) -> bool:
    return command in os.environ.get("_TYPER_COMPLETE_ARGS", "")


T = TypeVar("T")
R = TypeVar("R")



def dataclass_cli(func: Callable[[T], R]) -> Callable[..., R]:
    """Converts a function taking a dataclass as its first argument into a
    dataclass that can be called via `typer` as a CLI.

    Modified from:
    = https://gist.github.com/tbenthompson/9db0452445451767b59f5cb0611ab483#file-config-py
    """
    # The dataclass type is the first argument of the function.
    sig = inspect.signature(func)
    param = list(sig.parameters.values())[0]
    cls: Type[T] = param.annotation
    assert dataclasses.is_dataclass(cls)

    def wrapped(**conf: Any) -> R:
        # Load the config file if specified.

        # CLI options override the config file.

        # Convert back to the original dataclass type.
        arg = cast(T, cls(**conf))

        # Actually call the entry point function.
        return func(arg)

    # To construct the signature, we remove the first argument (self)
    # from the dataclass __init__ signature.
    signature = inspect.signature(cls.__init__)
    parameters = list(signature.parameters.values())

    if len(parameters) > 0 and parameters[0].name == "self":
        del parameters[0]

    setattr(wrapped, "__signature__", signature.replace(parameters=parameters))

    setattr(
        wrapped,
        "__doc__",
        func.__doc__ + "\n" + "" if func.__doc__ is not None else ...,
    )

    return wrapped
