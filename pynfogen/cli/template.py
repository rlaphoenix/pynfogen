import logging
from pathlib import Path

import click

from pynfogen.config import Files, Directories
from pynfogen.helpers import open_file


@click.group()
def template():
    """Manages template files."""


@template.command()
@click.argument("name", type=str)
@click.option("--bbcode", is_flag=True, default=False, help="Specify template as a BBCode Description template.")
def edit(name: str, bbcode: bool):
    """Edit a template file. If one does not exist, one will be created."""
    log = logging.getLogger("template")
    location = Path(str(Files.description if bbcode else Files.template).format(name=name))
    if not location.exists():
        log.info(f"Creating new template named {name}")
        location.parent.mkdir(exist_ok=True, parents=True)
        location.open("a").close()
    else:
        log.info(f"Opening existing template {name} for editing")
    open_file(str(location))


@template.command()
@click.argument("name", type=str)
@click.option("--bbcode", is_flag=True, default=False, help="Specify template as a BBCode Description template.")
@click.confirmation_option(prompt="Are you sure you want to delete the template?")
def delete(name: str, bbcode: bool):
    """Delete a template file."""
    log = logging.getLogger("template")
    location = Path(str(Files.description if bbcode else Files.template).format(name=name))
    if not location.exists():
        raise click.ClickException(f"Template {name} does not exist.")
    location.unlink()
    log.info(f"Template {name} has been deleted.")


@template.command(name="list")
def list_():
    """List all available templates."""
    found = 0
    for nfo in Directories.templates.glob("*.nfo"):
        print(nfo.stem, "-", "NFO", "Template")
        found += 1
    for txt in Directories.templates.glob("*.txt"):
        print(txt.stem, "-", "BBCode", "Template")
        found += 1
    if not found:
        raise click.ClickException("No templates found.")


@template.command()
def explore():
    """Open the template directory in your File Explorer."""
    open_file(str(Directories.templates))
