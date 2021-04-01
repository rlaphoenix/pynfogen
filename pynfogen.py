import os
import re
import yaml

from formatter import CustomFormats
from nfo import NFO


# Create NFO object
nfo = NFO()

# Set Configuration values from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    nfo.setConfig(yaml.load(f, Loader=yaml.FullLoader))

# Parse and Store NFO Data for use on templates
template_data = {
    "release_name": nfo.release_name,
    "title_name": nfo.title_name,
    "title_type_name": nfo.title_type_name,
    "title_year": nfo.title_year,
    "season": nfo.season,
    "episodes": nfo.episodes,
    "episode": nfo.episode,
    "episode_name": nfo.episode_name,
    "imdb": nfo.imdb,
    "tmdb": nfo.tmdb,
    "tvdb": nfo.tvdb,
    "preview_url": nfo.preview_url,
    "preview_images": nfo.preview_images,
    "banner_image": nfo.banner_image,
    "source": nfo.source,
    "note": nfo.note,
    "videos": nfo.getVideoPrint(nfo.videos),
    "videos_count": len(nfo.videos),
    "audios": nfo.getAudioPrint(nfo.audio),
    "audios_count": len(nfo.audio),
    "subtitles": nfo.getSubtitlePrint(nfo.subtitles),
    "subtitles_count": len(nfo.subtitles),
    "chapters": nfo.getChapterPrintShort(nfo.chapters),
    "chapters_count": len(nfo.chapters) if nfo.chapters else 0,
    "chapters_named": nfo.chapters and not nfo.chapters_numbered,
    "chapter_entries": nfo.getChapterPrint(nfo.chapters)
}


def parse_template(template: str, art: bool = False):
    template = CustomFormats().format(template, **template_data)
    # Apply Art template
    if art:
        with open(f"art/{nfo.art}.nfo", "rt", encoding="utf-8") as f:
            template = f.read().format(nfo=template)
    # Apply conditional logic
    for m in re.finditer(r"<\?([01])\?([\D\d]*?)\?>", template):
        template = template.replace(
            m.group(0), m.group(2) if int(m.group(1)) else "")
    # Strip unnecessary whitespace to reduce character count
    template = "\n".join([line.rstrip() for line in template.splitlines()])

    return template


# Parse NFO template
with open(f"templates/{nfo.title_type}.nfo", "rt", encoding="utf-8") as f:
    template = parse_template(f.read(), art=True)
print(template)
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt", encoding="utf-8") as f:
    # Save template to file with release name, next to input file
    f.write(template)
print(f"Generated NFO for {nfo.release_name}")

# Parse BBCode Description template
with open(f"templates/{nfo.title_type}.txt", "rt", encoding="utf-8") as f:
    template = parse_template(f.read())
print(template)
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt", encoding="utf-8") as f:
    # Save template to file with release name, next to input file
    f.write(template)
print(f"Generated BBCode Description for {nfo.release_name}")
