import os

import yaml

from pynfogen.nfo import NFO


def main():
    nfo = NFO()

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        nfo.set_config(**config)

    template_data = {
        "videos": nfo.get_video_print(nfo.videos),
        "audios": nfo.get_audio_print(nfo.audio),
        "subtitles": nfo.get_subtitle_print(nfo.subtitles),
        "chapters": nfo.get_chapter_print_short(nfo.chapters),
        "chapters_named": nfo.chapters and not nfo.chapters_numbered,
        "chapter_entries": nfo.get_chapter_print(nfo.chapters)
    }

    art = None
    if config.get("art") and os.path.exists(f"art/{config['art']}.nfo"):
        with open(f"art/{config['art']}.nfo", "rt") as f:
            art = f.read()

    with open(f"templates/{config['template']}.nfo", "rt") as f:
        template = f.read()
    nfo_txt = nfo.run(template, art=art, **template_data)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt") as f:
        f.write(nfo_txt)
    print(f"Generated NFO for {nfo.release_name}")

    with open(f"templates/{config['template']}.txt", "rt") as f:
        template = f.read()
    bb_txt = nfo.run(template, **template_data)
    with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt") as f:
        f.write(bb_txt)
    print(f"Generated BBCode Description for {nfo.release_name}")


if __name__ == "__main__":
    main()
