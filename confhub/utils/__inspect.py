import inspect
from inspect import FullArgSpec
from typing import Callable, Any, Dict


def inspect_get_full_arg_spec(func: Callable[..., Any]) -> Dict[str, Any]:
    signature = inspect.signature(func)
    result = {}

    for param_name, param in signature.parameters.items():
        default = param.default
        optional = default is not param.empty

        result[param_name] = {
            "is_optional": optional,
            "default": default if default is not param.empty else None
        }

    return result
