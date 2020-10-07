import os
import types
import textwrap
import pycountry
from pymediainfo import MediaInfo

# CONFIG
CFG = {
  "file": "file:///mnt/emby-red/tv/Sonic Underground/Sonic.Underground.S01.PAL.DVD.DD.2.0.MPEG-2.REMUX-RPG/Sonic.Underground.S01E01.Beginnings.Origins.Part.1.PAL.DVD.DD.2.0.MPEG-2.REMUX-RPG.mkv",
  "art": "rpg",                       # ASCII NFO art selector
  "type": "season",                   # movie, season, episode (this is the template selector)
  "title-name": "Sonic Underground",  # as appearing on imdb, or you're best judgment
  "title-year": "1999-2000",          # {first}-{last} or just {first} if it's still airing or a movie
  "imdb-id": "tt0230804",             # include the initial tt
  "tmdb-id": "tv/20992",              # must start with type crib, i.e. `tv/` or `movie/`
  "tvdb-id": 73634,                   # this is a number, not a title slug (e.g. `75978`, not `family-guy`)
  "season": 1,                        # recommended use cases: `1`, `V01`, `0`, `Specials`, `Compilations`, `Misc`
  "episodes": 40,                     # amount of full feature episodes available in the release
  "episode": "2",                     # used for "episode" type: the episode number of the input file above
  "episode-name": "Snow Job",         # used for "episode" type: the episode name of the input file above
  "imagebox-url": "https://imgbox.com/g/WFl98E7Iyg",
  "source": "R2 GBR Anchor Bay Ent. DVD-PHOENiX (Thanks!!)"
}

# Prepare config data
if CFG["file"].startswith("file://"):
  CFG["file"] = CFG["file"][7:]
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
videos = [x for x in mi.tracks if x.track_type == "Video"]
audios = [x for x in mi.tracks if x.track_type == "Audio"]
subtitles = [x for x in mi.tracks if x.track_type == "Text"]
chapters = [x for x in mi.tracks if x.track_type == "Menu"]

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
  ("imageboxUrl", CFG["imagebox-url"]),
  ("source", CFG["source"]),
  ("videoTracks", ["├ --"] if not videos else [[
    f"├ {pycountry.languages.get(alpha_2=t.language).name}, {t.format.replace('MPEG Video', 'MPEG-' + t.format_version.replace('Version ', ''))} ({t.format_profile}) {t.width}x{t.height} ({t.other_display_aspect_ratio[0]}) @ {t.other_bit_rate[0]}{f' ({t.bit_rate_mode})' if t.bit_rate_mode else ''}",
    f"│ {(f'{t.framerate_num}/{t.framerate_den}' if t.framerate_num else t.frame_rate)} FPS, {t.color_space}{t.chroma_subsampling.replace(':', '')}P{t.bit_depth}, {t.scan_type}"
  ] for t in videos]),
  ("videoTrackCount", len(videos)),
  ("audioTracks", ["├ --"] if not audios else [[
    f"├ {pycountry.languages.get(alpha_2=t.language).name}, {t.format} ({t.other_sampling_rate[0]}), {t.other_channel_s[0]} @ {t.other_bit_rate[0]}{f' ({t.bit_rate_mode})' if t.bit_rate_mode else ''}"
  ] for t in audios]),
  ("audioTrackCount", len(audios)),
  ("subtitleTracks", ["├ --"] if not subtitles else [[
    f"├ {t.title or pycountry.languages.get(alpha_2=t.language).name}, {t.format.replace('UTF-8', 'SubRip (SRT)')}"
  ] for t in subtitles]),
  ("subtitleTrackCount", len(subtitles)),
  ("chapterEntries", ["├ --"] if not chapters else [[
    f"├ {v}"
  ] for k,v in chapters[0].to_data().items() if ("1" + k.replace("_", "")).isdigit()]),
  ("chaptersCount", sum(1 for k,v in chapters[0].to_data().items() if ("1" + k.replace("_", "")).isdigit())),
]

# Load NFO template
NFO = []
with open(f"templates/{CFG['type']}.nfo", mode="rt", encoding="utf-8") as f:
  for line in f:
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
          VarValue = f"\n{pre}".join([f"\n{pre}".join([y for y in x]) for x in VarValue])
        else:
          VarValue = f"\n{pre}".join(VarValue)
      line = line.replace(VarName, VarValue)
    NFO.append(line)

NFO = "\n".join(NFO)

# apply art template
with open(f"art/{CFG['art']}.nfo", mode="rt", encoding="utf-8") as f:
  NFO = f.read().replace("%nfo%", NFO)

# save to NFO file
with open(os.path.join(os.path.dirname(CFG["file"]), f"{CFG['release-name']}.nfo"), "wt") as f:
  f.write(NFO)

print(f"Generated NFO for {CFG['release-name']}")