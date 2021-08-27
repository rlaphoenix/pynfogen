import codecs

import click
from dunamai import Version, Style
from unidecode import unidecode

from pynfogen import __version__
from pynfogen.cli.artwork import artwork
from pynfogen.cli.config import config
from pynfogen.cli.generate import generate
from pynfogen.cli.template import template


@click.group(context_settings=dict(
    help_option_names=["-?", "-h", "--help"],
    max_content_width=116  # max PEP8 line-width, -4 to adjust for initial indent
))
def cli() -> None:
    """
    \b
    pynfogen
    Scriptable MediaInfo-fed NFO Generator for Movies and TV.
    https://github.com/rlaphoenix/pynfogen
    """
    codecs.register_error("unidecode", lambda e: (
        unidecode(e.object.decode("utf8"))[e.start:e.end], e.end  # type: ignore
    ))


@cli.command()
def about() -> None:
    """Shows information about pynfogen."""
    print(
        "pynfogen - Python NFO Generator.\n"
        "\n"
        "pynfogen is a scriptable MediaInfo-fed NFO Generator for Movies and TV.\n"
        "See: https://github.com/rlaphoenix/pynfogen for more information."
    )


@cli.command()
def version() -> None:
    """Shows the version of the project."""
    try:
        v = Version.from_git().serialize(style=Style.SemVer)
    except RuntimeError:
        v = __version__
    print("pynfogen", v)


command: click.Command
for command in (artwork, config, generate, template):
    cli.add_command(command)
