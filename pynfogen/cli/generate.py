import os
from pathlib import Path
from typing import Tuple

import click
import yaml

from pynfogen.nfo import NFO


@click.command()
@click.argument("template", type=str)
@click.argument("file", type=str)
@click.option("-a", "--artwork", type=str, default=None, help="Artwork to use.")
@click.option("-s", "--season", type=str, default=None,
              help="TV Show Season Number (or name).")
@click.option("-e", "--episode", type=(int, str), default=[None] * 2,
              help="TV Show Episode Number and Title.")
@click.option("-imdb", type=str, default=None, help="IMDB ID (including 'tt').")
@click.option("-tmdb", type=str, default=None, help="TMDB ID (including 'tv/' or 'movie/').")
@click.option("-tvdb", type=int, default=None, help="TVDB ID ('73244' not 'the-office-us').")
@click.option("-S", "--source", type=str, default=None, help="Source information.")
@click.option("-N", "--notes", type=str, default=None, help="Notes/special information.")
@click.pass_obj
def generate(obj, file: str, template: str, artwork: str = None, season: str = None, episode: Tuple[int, str] = None,
             imdb: str = None, tmdb: str = None, tvdb: int = None, source: str = None, notes: str = None):
    """
    Generate an NFO for a file.
    It's recommended to specify both -e and -et if not a season.
    Whether the values get used is up to the template to decide.
    """
    if season.isdigit():
        season = int(season)

    nfo = NFO()

    config = obj["config_path"]
    if config.exists():
        with config.open() as f:
            nfo.set_config(
                file, season, episode,
                **dict(
                    imdb=imdb,
                    tmdb=tmdb,
                    tvdb=tvdb,
                    source=source,
                    notes=notes,
                    **yaml.load(f, Loader=yaml.FullLoader)
                )
            )

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
