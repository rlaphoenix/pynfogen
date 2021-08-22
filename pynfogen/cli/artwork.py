import logging
from pathlib import Path

import click

from pynfogen.config import Files, Directories
from pynfogen.helpers import open_file


@click.group()
def artwork() -> None:
    """Manages artwork files."""


@artwork.command()
@click.argument("name", type=str)
def edit(name: str) -> None:
    """Edit an artwork file. If one does not exist, one will be created."""
    log = logging.getLogger("artwork")
    location = Path(str(Files.artwork).format(name=name))
    if not location.exists():
        log.info(f"Creating new artwork named {name}")
        location.parent.mkdir(exist_ok=True, parents=True)
        location.open("a").close()
    else:
        log.info(f"Opening existing artwork {name} for editing")
    open_file(str(location))


@artwork.command()
@click.argument("name", type=str)
@click.confirmation_option(prompt="Are you sure you want to delete the artwork?")
def delete(name: str) -> None:
    """Delete an artwork file."""
    log = logging.getLogger("artwork")
    location = Path(str(Files.artwork).format(name=name))
    if not location.exists():
        raise click.ClickException(f"Artwork {name} does not exist.")
    location.unlink()
    log.info(f"Artwork {name} has been deleted.")


@artwork.command(name="list")
def list_() -> None:
    """List all available artworks."""
    found = 0
    for nfo in Directories.artwork.glob("*.nfo"):
        print(nfo.stem)
        found += 1
    if not found:
        raise click.ClickException("No artworks found.")


@artwork.command()
def explore() -> None:
    """Open the artwork directory in your File Explorer."""
    open_file(str(Directories.artwork))
