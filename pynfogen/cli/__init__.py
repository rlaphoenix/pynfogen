from pathlib import Path

import click
from appdirs import user_data_dir
from dunamai import Version, Style

from pynfogen.cli.config import config


@click.group(context_settings=dict(
    help_option_names=["-?", "-h", "--help"],
    max_content_width=116  # max PEP8 line-width, -4 to adjust for initial indent
))
@click.pass_context
def cli(ctx):
    user_dir = Path(user_data_dir("pynfogen", "PHOENiX"))
    config_path = user_dir / "config.yml"
    ctx.obj = {
        "user_dir": user_dir,
        "config_path": config_path,
        "templates": user_dir / "templates"
    }


@cli.command()
def about():
    """Shows information about pynfogen."""
    print(
        "pynfogen - Python NFO Generator.\n"
        "\n"
        "pynfogen is a scriptable MediaInfo-fed NFO Generator for Movies and TV.\n"
        "See: https://github.com/rlaphoenix/pynfogen for more information."
    )


@cli.command()
def version():
    """Shows the version of the project."""
    print("pynfogen", Version.from_git().serialize(style=Style.SemVer))


cli.add_command(config)
