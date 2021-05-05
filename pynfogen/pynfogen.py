import os

import yaml

from pynfogen.nfo import NFO


def main():
    nfo = NFO()

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
        nfo.set_config(yaml.load(f, Loader=yaml.FullLoader))

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
        "videos": nfo.get_video_print(nfo.videos),
        "videos_count": len(nfo.videos),
        "audios": nfo.get_audio_print(nfo.audio),
        "audios_count": len(nfo.audio),
        "subtitles": nfo.get_subtitle_print(nfo.subtitles),
        "subtitles_count": len(nfo.subtitles),
        "chapters": nfo.get_chapter_print_short(nfo.chapters),
        "chapters_count": len(nfo.chapters) if nfo.chapters else 0,
        "chapters_named": nfo.chapters and not nfo.chapters_numbered,
        "chapter_entries": nfo.get_chapter_print(nfo.chapters)
    }

    art = None
    if nfo.art and os.path.exists(f"art/{nfo.art}.nfo"):
        with open(f"art/{nfo.art}.nfo", "rt") as f:
            art = f.read()

    with open(f"templates/{nfo.title_type}.nfo", "rt") as f:
        template = nfo.run(f.read(), art=art, **template_data)
    print(template)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt") as f:
        f.write(template)
    print(f"Generated NFO for {nfo.release_name}")

    with open(f"templates/{nfo.title_type}.txt", "rt") as f:
        template = nfo.run(f.read(), **template_data)
    print(template)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt") as f:
        f.write(template)
    print(f"Generated BBCode Description for {nfo.release_name}")


def cli():
    # cli will just do what main does for now
    main()


if __name__ == "__main__":
    main()
