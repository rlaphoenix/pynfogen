import os

import yaml

from pynfogen.nfo import NFO


def main():
    nfo = NFO()

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
        nfo.set_config(yaml.load(f, Loader=yaml.FullLoader))

    template_data = {
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
        template = f.read()
    nfo_txt = nfo.run(template, art=art, **template_data)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt") as f:
        f.write(nfo_txt)
    print(f"Generated NFO for {nfo.release_name}")

    with open(f"templates/{nfo.title_type}.txt", "rt") as f:
        template = f.read()
    bb_txt = nfo.run(template, **template_data)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt") as f:
        f.write(bb_txt)
    print(f"Generated BBCode Description for {nfo.release_name}")


def cli():
    # cli will just do what main does for now
    main()


if __name__ == "__main__":
    main()
