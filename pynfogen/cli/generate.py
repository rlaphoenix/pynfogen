import os
from pathlib import Path
from typing import Optional, Any

import click

from pynfogen.config import config, Files
from pynfogen.nfo import NFO


@click.group(context_settings=dict(default_map=config.get("generate", {})))
@click.argument("file", type=str)
@click.option("-a", "--artwork", type=str, default=None, help="Artwork to use.")
@click.option("-imdb", type=str, default=None, help="IMDB ID (including 'tt').")
@click.option("-tmdb", type=str, default=None, help="TMDB ID (including 'tv/' or 'movie/').")
@click.option("-tvdb", type=int, default=None, help="TVDB ID ('73244' not 'the-office-us').")
@click.option("-S", "--source", type=str, default=None, help="Source information.")
@click.option("-N", "--note", type=str, default=None, help="Notes/special information.")
@click.option("-P", "--preview", type=str, default=None, help="Preview information, typically an URL.")
@click.pass_context
def generate(*_: Any, **__: Any) -> None:
    """Generate an NFO and Description for a release."""


@generate.command(name="season")
@click.argument("season", type=str)
def season_(season: NFO.SEASON_T) -> dict:
    """
    Generate an NFO and Description for a season release.

    \b
    It's best practice to provide the first-most file that best represents the majority of the season.
    E.g., If Episode 1 and 2 has a fault not found on Episodes 3-9, then provide Episode 3.

    The season argument can be a Season Name or a Season Number, it's up to you. You may even provide
    a season name that also contains the Season Number e.g. "1: The Beginning" if you prefer. Just
    remember that it's up to the template on whether or not the result looks good or not.
    """
    if isinstance(season, str) and season.isdigit():
        season = int(season)
    return {"season": season}


@generate.command(name="episode")
@click.argument("episode", type=int)
@click.argument("title", type=str, default=None)
@click.argument("season", type=str, default=None)
def episode_(episode: int, title: str, season: NFO.SEASON_T) -> dict:
    """
    Generate an NFO and Description for a single-episode release.

    The episode title is optional but highly recommended. If there is no episode name like cases with
    Daily TV Shows and such, you may want to put the original Air Date as the Episode Name. It's
    recommended in such case to use ISO 8601 format; YYYY-MM-DD format.

    The season argument can be a Season Name or a Season Number, it's up to you. You may even provide
    a season name that also contains the Season Number e.g. "1: The Beginning" if you prefer. Just
    remember that it's up to the template on whether or not the result looks good or not.
    """
    if isinstance(season, str) and season.isdigit():
        season = int(season)
    return {
        "season": season,
        "episode": (episode, title or None)
    }


@generate.command()
def movie() -> dict:
    """Generate an NFO and Description for a movie release."""
    return {}


@generate.result_callback()
@click.pass_context
def generator(ctx: click.Context, args: dict, file: str, artwork: Optional[str], imdb: Optional[str],
              tmdb: Optional[str], tvdb: Optional[int], source: Optional[str], note: Optional[str],
              preview: Optional[str], *_: Any, **__: Any) -> None:
    if not isinstance(ctx, click.Context) or not ctx.invoked_subcommand:
        raise ValueError("Generator called directly, or not used as part of the generate command group.")
    if not os.path.exists(file):
        raise click.ClickException("The provided file or folder path does not exist.")

    nfo = NFO()
    nfo.set_config(
        str(Path(file).resolve()),
        **dict(
            imdb=imdb,
            tmdb=tmdb,
            tvdb=tvdb,
            source=source,
            note=note,
            preview=preview,
            **args,
            **config
        )
    )

    template_vars = {
        "videos_pretty": nfo.get_video_print(nfo.videos),
        "audio_pretty": nfo.get_audio_print(nfo.audio),
        "subtitles_pretty": nfo.get_subtitle_print(nfo.subtitles),
        "chapters_yes_no": nfo.get_chapter_print_short(nfo.chapters),
        "chapters_named": nfo.chapters and not nfo.chapters_numbered,
        "chapter_entries": nfo.get_chapter_print(nfo.chapters)
    }

    template = ctx.invoked_subcommand

    if artwork:
        artwork_path = Path(str(Files.artwork).format(name=artwork))
        if not artwork_path.exists():
            raise click.ClickException(f"No artwork named {artwork} exists.")
        artwork = artwork_path.read_text()

    template_path = Path(str(Files.template).format(name=template))
    if not template_path.exists():
        raise click.ClickException(f"No template named {template} exists.")
    template_data = template_path.read_text()

    nfo_txt = nfo.run(template_data, art=artwork, **template_vars)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt", encoding="utf8") as f:
        f.write(nfo_txt)
    print(f"Generated NFO for {nfo.release_name}")

    description_path = Path(str(Files.description).format(name=template))
    if description_path.exists():
        description_data = description_path.read_text()
        bb_txt = nfo.run(description_data, art=None, **template_vars)
        with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt", encoding="utf8") as f:
            f.write(bb_txt)
        print(f"Generated BBCode Description for {nfo.release_name}")
