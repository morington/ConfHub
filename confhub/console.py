import inspect
from argparse import ArgumentParser, Namespace
from typing import Optional, Any, Sequence, Dict

import structlog

from confhub.core.error import confhub_error, ConfhubError
from confhub import commands
from confhub.utils.__inspect import inspect_get_full_arg_spec

logger: structlog.BoundLogger = structlog.getLogger('confhub')


class CommandLineInterface:
    def __init__(self, prog: Optional[str] = None, version: Optional[str] = None) -> None:
        self._generate_args(prog, version)

    def _generate_args(self, prog: Optional[str] = None, version: Optional[str] = None) -> None:
        def add_options(_parser: ArgumentParser, function_arguments: Dict[str, Any]):
            kwargs_opts = {
                "folder": dict(
                    kwargs=dict(
                        type=str,
                        help="Folder is specified",
                    ),
                ),
            }

            for arg, metadata in function_arguments.items():
                options = kwargs_opts.get(arg)

                if options:
                    if metadata.get('is_optional'):
                        flags = options.get('flags')
                        if not flags:
                            raise ConfhubError(f"Optional flags not found for `{arg}`")

                        _parser.add_argument(*flags, **options.get('kwargs'))
                    else:
                        subparser.add_argument(arg, **options.get('kwargs'))

        prog_version = f"{prog} v{version}"
        parser = ArgumentParser(prog=prog, description=f"{prog_version} help")

        parser.add_argument(
            "--version", action="version", version=prog_version
        )
        parser.add_argument(
            "--raiser",
            action="store_true",
            help="Raise a full stack trace on error",
        )

        subparsers = parser.add_subparsers()

        for fn in [getattr(commands, n) for n in dir(commands)]:
            if (
                inspect.isfunction(fn)
                and fn.__name__[0] != "_"
                and fn.__module__ == "confhub.commands"
            ):
                args: Dict[str, Any] = inspect_get_full_arg_spec(fn)

                help_ = fn.__doc__
                if help_:
                    help_text = []
                    for line in help_.split("\n"):
                        if not line.strip():
                            continue
                        else:
                            help_text.append(line.strip())
                else:
                    help_text = []

                subparser = subparsers.add_parser(fn.__name__, help=" ".join(help_text))
                add_options(_parser=subparser, function_arguments=args)
                subparser.set_defaults(cmd=(fn, args.keys()))
        self.parser = parser

    def run(self, options: Namespace) -> None:
        fn, args = options.cmd

        try:
            fn(*[getattr(options, arg, None) for arg in args])
        except Exception as e:
            if options.raiser:
                raise
            else:
                confhub_error(str(e), args=args)

    def main(self, argv: Optional[Sequence[str]] = None) -> None:
        options = self.parser.parse_args(argv)

        if not hasattr(options, "cmd"):
            # see http://bugs.python.org/issue9253, argparse
            # behavior changed incompatibly in py3.3
            self.parser.error("too few arguments")
        else:
            self.run(options)


def main(argv: Optional[Sequence[str]] = None, prog: Optional[str] = None, version: Optional[str] = None) -> None:
    CommandLineInterface(prog=prog, version=version).main(argv=argv)
