import os
from pathlib import Path

import click
import yaml

from pynfogen.nfo import NFO


@click.command()
@click.argument("template", type=str)
@click.argument("file", type=str)
@click.option("-a", "--artwork", type=str, default=None, help="Artwork to use.")
@click.pass_obj
def generate(obj, file: str, template: str, artwork: str = None):
    """Generate an NFO for a file."""
    nfo = NFO()

    config = obj["config_path"]
    if config.exists():
        with config.open() as f:
            nfo.set_config(file, **yaml.load(f, Loader=yaml.FullLoader))

    template_data = {
        "videos": nfo.get_video_print(nfo.videos),
        "audios": nfo.get_audio_print(nfo.audio),
        "subtitles": nfo.get_subtitle_print(nfo.subtitles),
        "chapters": nfo.get_chapter_print_short(nfo.chapters),
        "chapters_named": nfo.chapters and not nfo.chapters_numbered,
        "chapter_entries": nfo.get_chapter_print(nfo.chapters)
    }

    if artwork:
        artwork = Path(obj["artworks"] / f"{artwork}.nfo")
        if not artwork.exists():
            raise click.ClickException(f"No artwork named {artwork.stem} exists.")
        artwork = artwork.read_text()

    template = Path(obj["templates"] / f"{template}.nfo")
    if not template.exists():
        raise click.ClickException(f"No template named {template.stem} exists.")
    template = template.read_text()

    nfo_txt = nfo.run(template, art=artwork, **template_data)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt") as f:
        f.write(nfo_txt)
    print(f"Generated NFO for {nfo.release_name}")

    template = Path(obj["templates"] / f"{template}.txt")
    if template.exists():
        template = template.read_text()
        bb_txt = nfo.run(template, **template_data)
        with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt") as f:
            f.write(bb_txt)
        print(f"Generated BBCode Description for {nfo.release_name}")
