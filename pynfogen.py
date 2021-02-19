import os
import re
import yaml

from formatter import CustomFormats
from helpers import scrape
from nfo import NFO


# Create NFO object
nfo = NFO()

# Set Configuration values from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    nfo.setConfig(yaml.load(f, Loader=yaml.FullLoader))

# Parse NFO template
with open(f"templates/{nfo.title_type}.nfo", "rt", encoding="utf-8") as f:
    template = f.read()

# Apply formatting value logic
template = CustomFormats().format(
    template,
    release_name=nfo.release_name,
    title_name=nfo.title_name,
    title_type_name=nfo.title_type_name,
    title_year=nfo.title_year,
    season=nfo.season,
    episodes=nfo.episodes,
    episode=nfo.episode,
    episode_name=nfo.episode_name,
    imdb=nfo.imdb,
    tmdb=nfo.tmdb,
    tvdb=nfo.tvdb,
    preview_url=nfo.preview_url,
    preview_images=nfo.preview_images,
    source=nfo.source,
    note=nfo.note,
    videos=nfo.getVideoPrint(nfo.videos),
    videos_count=len(nfo.videos),
    audios=nfo.getAudioPrint(nfo.audio),
    audios_count=len(nfo.audio),
    subtitles=nfo.getSubtitlePrint(nfo.subtitles),
    subtitles_count=len(nfo.subtitles),
    chapters=nfo.getChapterPrintShort(nfo.chapters),
    chapters_count=len(nfo.chapters) if nfo.chapters else 0,
    chapters_named=nfo.chapters and not nfo.chapters_numbered,
    chapter_entries=nfo.getChapterPrint(nfo.chapters)
)

# Apply Art template
with open(f"art/{nfo.art}.nfo", "rt", encoding="utf-8") as f:
    template = f.read().format(nfo=template)

# Apply conditional logic
for i, m in enumerate(re.finditer(r"<\?(0|1)\?([\D\d]*?)\?>", template)):
    template = template.replace(
        m.group(0), m.group(2) if int(m.group(1)) else "")

# Strip unnecessary whitespace to reduce character count
template = "\n".join([line.rstrip() for line in template.splitlines()])

print(template)

# Save template to file with release name, next to input file
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt", encoding="utf-8") as f:
    f.write(template)

print(f"Generated NFO for {nfo.release_name}")

# generate bb code description
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt", encoding="utf-8") as f:
    description = ""
    description += f"[code]\n{template}\n[/code]"
    f.write(description)

print(f"Generated BBCode Description for {nfo.release_name}")
