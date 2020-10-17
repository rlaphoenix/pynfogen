import glob
import os
import re
import textwrap
import pycountry
import requests
import yaml
from pymediainfo import MediaInfo
from pyd2v import D2V
from pvsfunc.helpers import anti_file_prefix, get_video_codec, get_d2v


def scrape(url):
    return requests.get(
        url=url,
        headers={
            # pretend to be a normal firefox user, we can't leave anything to chance
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "UPGRADE-INSECURE-REQUESTS": "1"
        }
    ).text


# CONFIG, this is edited in `config.yml` next to pynfogen.py
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    CFG = yaml.load(f, Loader=yaml.FullLoader)
    if not CFG:
        raise ValueError("config.yml empty??")
    if "imagebox-url" in CFG:
        raise Exception(
            "You have imagebox-url in your config.yml, this was recently changed to preview-url"
            "Please change it to preview-url to continue. This warning will be removed! (idk when)"
        )

# Prepare config data
CFG["file"] = anti_file_prefix(CFG["file"])
if CFG["type"] in ["episode", "movie"]:
    CFG["release-name"] = os.path.splitext(os.path.basename(CFG["file"]))[0]
if CFG["type"] in ["season"]:
    CFG["release-name"] = os.path.basename(os.path.dirname(CFG["file"]))
CFG["title-type"] = {
    "season": "TV Series",
    "episode": "TV Series",
    "movie": "Movie"
}[CFG["type"]]

# Get MediaInfo
mi = MediaInfo.parse(CFG["file"])
general = [x for x in mi.tracks if x.track_type == "General"][0]
videos = [x for x in mi.tracks if x.track_type == "Video"]
audios = [x for x in mi.tracks if x.track_type == "Audio"]
subtitles = [x for x in mi.tracks if x.track_type == "Text"]
chapters = [x for x in mi.tracks if x.track_type == "Menu"]
chapters_numbered = False

# Parse chapters
if chapters:
    chapters = [v for k, v in chapters[0].to_data().items() if ("1" + k.replace("_", "")).isdigit()]
    chapters_numbered = sum(1 for i, x in enumerate(chapters) if x.split(":", 1)[-1] in [f"Chapter {i+1}", f"Chapter {str(i+1).zfill(2)}"]) == len(chapters)

# Auto set CFG entries based on MediaInfo data, if present
if general.imdb:
    CFG["imdb-id"] = general.imdb
if general.tmdb:
    CFG["tmdb-id"] = general.tmdb
if general.tvdb:
    CFG["tvdb-id"] = general.tvdb
if general.title:
    tv_title = re.search("^(.*?) S(\\d+)E(\\d+) (.*)$", general.title)
    movie_title = re.search("^(.*?) \\((\\d{4})\)$", general.title)
    if tv_title:
        CFG["title-name"], CFG["season"], CFG["episode"], CFG["episode-name"] = tv_title.groups()
        CFG["season"] = int(CFG["season"])
        CFG["episode"] = int(CFG["episode"])
        CFG["episodes"] = len(glob.glob(os.path.join(os.path.dirname(CFG["file"]), "*.mkv")))
        imdb_page = scrape(f"https://www.imdb.com/title/{CFG['imdb-id']}")
        imdb_year = re.search("TV Series (\\d{4}–\\d{4})", imdb_page)
        if not imdb_year:
            imdb_year = re.search("TV Series (\\d{4})–", imdb_page)
        if not imdb_year:
            imdb_year = re.search("TV Series (\\d{4})", imdb_page)
        CFG["title-year"] = imdb_year.group(1)
    elif movie_title:
        CFG["title-name"], CFG["title-year"] = movie_title.groups()
        CFG["type"] = "movie"

# Get VST state and percentage of interlaced frames in video
interlaced_percent = None
vst = False
if get_video_codec(CFG["file"]) in ["V_MPEG1", "V_MPEG2"]:
    # make sure a d2v file for this video exists
    CFG["file"] = get_d2v(CFG["file"])
    # parse d2v file with pyd2v
    d2v = D2V(CFG["file"])
    # get every frames' flag data, this contains information on displaying frames
    # add vob and cell number to each frames flag data as well
    flags = [f for line in [
        [dict(**y, vob=x["vob"], cell=x["cell"]) for y in x["flags"]] for x in d2v.data
    ] for f in line]
    interlaced_percent = (sum(1 for f in flags if not f["progressive_frame"]) / len(flags)) * 100
    if interlaced_percent == 100:
        interlaced_percent = "Interlaced (CST)"
    else:
        interlaced_percent = f"{round(interlaced_percent, 2)}% Interlaced (VST)"
        vst = True
    for ext in ["log", "d2v", "mpg"]:
        os.unlink(os.path.splitext(CFG["file"])[0] + "." + ext)

# Configure Variables

VARS = [
    ("releaseName", [x.center(70) for x in textwrap.wrap(CFG["release-name"], 68)]),
    ("titleName", CFG["title-name"]),
    ("titleType", CFG["title-type"]),
    ("titleYear", CFG["title-year"]),
    ("seasonNum", CFG["season"]),
    ("episodeCount", CFG["episodes"]),
    ("episodeNum", CFG["episode"]),
    ("episodeName", CFG["episode-name"]),
    ("imdbId", CFG["imdb-id"]),
    ("tmdbId", CFG["tmdb-id"]),
    ("tvdbId", CFG["tvdb-id"]),
    ("imageboxUrl", CFG["preview-url"]),
    ("source", textwrap.wrap(CFG["source"], 68) if CFG["source"] else None),
    ("videoTracks", ["--"] if not videos else [[
        f"- {pycountry.languages.get(alpha_2=t.language).name}, {'MPEG-' + t.format_version.replace('Version ', '') if t.format == 'MPEG Video' else t.format} ({t.format_profile}) {t.width}x{t.height} ({t.other_display_aspect_ratio[0]}) @ {t.other_bit_rate[0]}{f' ({t.bit_rate_mode})' if t.bit_rate_mode else ''}",
        f"  {(f'{t.framerate_num}/{t.framerate_den}' if t.framerate_num else t.frame_rate)} FPS ({'VFR' if vst else t.frame_rate_mode}), {t.color_space}{t.chroma_subsampling.replace(':', '')}P{t.bit_depth}, {interlaced_percent if interlaced_percent else t.scan_type}"
    ] for t in videos]),
    ("videoTrackCount", len(videos)),
    ("audioTracks", ["--"] if not audios else [[('  ' + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(
        f"- {t.title if t.title and 'Commentary' in t.title else pycountry.languages.get(alpha_2=t.language).name}, {t.format} {float(sum({'LFE': 0.1}.get(x, 1) for x in t.channel_layout.split(' ')))} @ {t.other_bit_rate[0]}{f' ({t.bit_rate_mode})' if t.bit_rate_mode else ''}",
        64
    ))] for t in audios]),
    ("audioTrackCount", len(audios)),
    ("subtitleTracks", ["--"] if not subtitles else [[('  ' + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(
        f"- {t.title or pycountry.languages.get(alpha_2=t.language).name}, {t.format.replace('UTF-8', 'SubRip (SRT)')}",
        64
    ))] for t in subtitles]),
    ("subtitleTrackCount", len(subtitles)),
    ("chapters", "No" if not chapters else f"Yes ({f'Numbered (01-{str(len(chapters)).zfill(2)})' if chapters_numbered else 'Named'})"),
    ("chapterEntries", ["--"] if not chapters else [[
        f"- {v}"
    ] for v in chapters]),
    ("chaptersCount", 0 if not chapters else len(chapters)),
    ("chaptersNamed", chapters and not chapters_numbered),
    ("note", textwrap.wrap(CFG["note"], 68) if CFG["note"] else None),
]

# Load NFO template
NFO = []
with open(f"templates/{CFG['type']}.nfo", mode="rt", encoding="utf-8") as f:
    fs = f.read()
    conditional_regex = re.compile('<\?(\w+)\?([\D\d]*?)\?>')
    for i, m in enumerate(re.finditer(conditional_regex, fs)):
        VarValue = [x for k,x in VARS if k == m.group(1)][0]
        fs = re.sub(
            '<\?' + m.group(1) + '\?([\D\d]*?)\?>',
            m.group(2) if VarValue else "",
            fs
        )
    for line in fs.splitlines():
        line = line.rstrip("\n\r")
        for VarName, VarValue in VARS:
            VarName = f"%{VarName}%"
            if VarName not in line:
                continue
            pre = line[:line.index(VarName)]
            if isinstance(VarValue, int):
                VarValue = str(VarValue)
            elif isinstance(VarValue, list):
                if isinstance(VarValue[0], list):
                    VarValue = f"\n{pre}".join([
                        f"\n{pre}".join([
                            y for y in x
                        ]) for x in VarValue
                    ])
                else:
                    VarValue = f"\n{pre}".join(VarValue)
            line = line.replace(VarName, VarValue)
        NFO.append(line)

NFO = "\n".join(NFO)

# apply art template
with open(f"art/{CFG['art']}.nfo", mode="rt", encoding="utf-8") as f:
    NFO = f.read().replace("%nfo%", NFO)

# save to NFO file
with open(os.path.join(os.path.dirname(CFG["file"]), f"{CFG['release-name']}.nfo"), "wt", encoding="utf-8") as f:
    f.write(NFO)

# generate bb code description
with open(os.path.join(os.path.dirname(CFG["file"]), f"{CFG['release-name']}.description.txt"), "wt",
          encoding="utf-8") as f:
    DESC = ""
    if CFG["preview-url"]:
        supported_domains = ["imgbox.com", "beyondhd.co"]
        for domain in supported_domains:
            if domain in CFG["preview-url"].lower():
                page = scrape(CFG["preview-url"])
                DESC += "[align=center]\n"
                if domain == "imgbox.com":
                    regex = 'src="(https://thumbs2.imgbox.com.+/)(\\w+)_b.([^"]+)'
                    template = "[URL=https://imgbox.com/{1}][IMG]{0}{1}_t.{2}[/IMG][/URL]"
                if domain == "beyondhd.co":
                    regex = '/image/([^"]+)"\\D+src="(https://beyondhd.co/images.+/(\\w+).md.[^"]+)'
                    template = "[URL=https://beyondhd.co/image/{0}][IMG]{1}[/img][/URL]"
                for i, m in enumerate(re.finditer(regex, page)):
                    DESC += template.format(*m.groups())
                    if (i % 2) != 0:
                        DESC += "\n"
                if not DESC.endswith("\n"):
                    DESC += "\n"
                DESC += "[/align]\n"
    DESC += f"[code]\n{NFO}\n[/code]"
    f.write(DESC)

print(f"Generated NFO for {CFG['release-name']}")
