import codecs
import gzip
from datetime import datetime
from pathlib import Path

import click
import jsonpickle
import toml
from click_default_group import DefaultGroup
from dunamai import Style, Version
from unidecode import unidecode

from pynfogen import __version__
from pynfogen.cli.artwork import artwork
from pynfogen.cli.config import config
from pynfogen.cli.generate import generate
from pynfogen.cli.template import template
from pynfogen.config import Directories, Files
from pynfogen.config import config as config_data


@click.group(
    cls=DefaultGroup, default="generate", default_if_no_args=True,
    context_settings=dict(
        help_option_names=["-?", "-h", "--help"],
        max_content_width=116  # max PEP8 line-width, -4 to adjust for initial indent
    )
)
def cli() -> None:
    """
    \b
    pynfogen
    Scriptable MediaInfo-fed NFO Generator for Movies and TV.
    https://github.com/rlaphoenix/pynfogen
    """
    codecs.register_error("unidecode", lambda e: (
        unidecode(
            e.object.decode("utf8") if isinstance(e.object, bytes) else e.object
        )[e.start:e.end],
        e.end
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


@cli.command()
@click.argument("out_dir", type=Path)
def export(out_dir: Path) -> None:
    """Export all configuration, artwork, and templates."""
    if not out_dir or not out_dir.is_dir():
        raise click.ClickException("Save Path must be directory.")

    art = {x.stem: x.read_text(encoding="utf8") for x in Directories.artwork.glob("*.nfo")}
    nfo = {x.stem: x.read_text(encoding="utf8") for x in Directories.templates.glob("*.nfo")}
    txt = {x.stem: x.read_text(encoding="utf8") for x in Directories.templates.glob("*.txt")}
    json = jsonpickle.dumps({
        "version": 1,
        "config": config_data,
        "art": art,
        "nfo": nfo,
        "txt": txt
    })

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"pynfogen.export.{datetime.now().strftime('%Y%m%d-%H%M%S')}.json.gz"

    out_path.write_bytes(gzip.compress(json.encode("utf8")))

    print(f"Successfully exported to: {out_path}")


@cli.command(name="import")
@click.argument("file", type=Path)
def import_(file: Path):
    """
    Import all configuration, artwork, and templates from export.

    The configuration will be overwritten in it's entirety.
    Current artwork and template files will only be overwritten if
    they have the same name.
    """
    if not file or not file.exists():
        raise click.ClickException("File path does not exist.")

    decompress = gzip.open(file).read().decode("utf8")
    json = jsonpickle.decode(decompress)

    Files.config.parent.mkdir(parents=True, exist_ok=True)
    Directories.artwork.mkdir(parents=True, exist_ok=True)
    Directories.templates.mkdir(parents=True, exist_ok=True)

    Files.config.write_text(toml.dumps(json["config"]))
    print("Imported Configuration")

    for name, data in json["art"].items():
        path = (Directories.artwork / name).with_suffix(".nfo")
        path.write_text(data, encoding="utf8")
        print(f"Imported Artwork: {name}")

    for name, data in json["nfo"].items():
        path = (Directories.templates / name).with_suffix(".nfo")
        path.write_text(data, encoding="utf8")
        print(f"Imported NFO Template: {name}")

    for name, data in json["txt"].items():
        path = (Directories.templates / name).with_suffix(".txt")
        path.write_text(data, encoding="utf8")
        print(f"Imported Description Template: {name}")

    print(f"Successfully Imported from {file}!")


command: click.Command
for command in (artwork, config, generate, template):
    cli.add_command(command)
