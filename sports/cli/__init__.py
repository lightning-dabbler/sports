import logging
import sys
from importlib import import_module

import click
from loguru import logger


# Taken from: https://github.com/indico/indico/blob/master/indico/cli/util.py
# See licenses/CERN.txt for the relevant license statement
class LazyGroup(click.Group):
    """
    A click Group that imports the actual implementation only when
    needed.  This allows for more resilient CLIs where the top-level
    command does not fail when a subcommand is broken enough to fail
    at import time.
    """

    def __init__(self, import_name, **kwargs):
        self._import_name = import_name
        super(LazyGroup, self).__init__(**kwargs)
        self._module_imple = None

    @property
    def _impl(self):
        if self._module_imple is None:
            module, name = self._import_name.split(":", 1)
            self._module_imple = getattr(import_module(module), name)
        return self._module_imple

    def get_command(self, ctx, cmd_name):
        return self._impl.get_command(ctx, cmd_name)

    def list_commands(self, ctx):
        return self._impl.list_commands(ctx)

    def invoke(self, ctx):
        return self._impl.invoke(ctx)

    def get_usage(self, ctx):
        return self._impl.get_usage(ctx)

    def get_params(self, ctx):
        return self._impl.get_params(ctx)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-s", "--serialize", is_flag=True, default=False)
def cli(verbose, serialize):
    """This is the main sports entrypoint"""
    logger.remove()
    if verbose:
        cli_log_level = max(logging.ERROR - min((10 * verbose), 40), 5)
    else:
        cli_log_level = 20
    if serialize:
        logger.add(
            sys.stderr, level=cli_log_level, serialize=serialize, format="{message}", backtrace=False, diagnose=False
        )
    else:
        logger.add(
            sys.stderr,
            level=cli_log_level,
            serialize=serialize,
            format="<level>[{level}]</level> <green>[{time}]</green> <level>{message}</level>",
            backtrace=True,
            diagnose=True,
        )
    logger.debug("Log level: {log_level}", verbose=verbose, log_level=cli_log_level)


@cli.group(cls=LazyGroup, import_name="sports.cli.fox_sports:cli")
def fox_sports():
    """Executes Fox Sports related CLI commands"""
