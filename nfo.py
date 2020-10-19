import glob
import os
import re
import textwrap

import pycountry
from pvsfunc.helpers import anti_file_prefix, get_d2v
from pyd2v import D2V
from pymediainfo import MediaInfo

from helpers import scrape


class NFO:

    TEMPLATE_VAR_TO_CLASS_VAR_MAP = {
        "releaseName": "release_name",
        "titleName": "title_name",
        "titleType": "title_type_name",
        "titleYear": "title_year",
        "seasonNum": "season",
        "episodeCount": "episodes",
        "episodeNum": "episode",
        "episodeName": "episode_name",
        "imdbId": "imdb",
        "tmdbId": "tmdb",
        "tvdbId": "tvdb",
        "imageboxUrl": "preview_url",
        "source": "source",
        "note": "note",
        "videoTracks": "videos",
        "videoTrackCount": "videos",
        "audioTracks": "audio",
        "audioTrackCount": "audio",
        "subtitleTracks": "subtitles",
        "subtitleTrackCount": "subtitles",
        "chapters": "chapters",
        "chapterEntries": "chapters",
        "chaptersCount": "chapters",
        "chaptersNamed": "chapters",
    }

    AUDIO_CHANNEL_LAYOUT_WEIGHT = {
        "LFE": 0.1
    }

    def __init__(self):
        self.media_info = None
        self.art = None
        self.file = None
        self.imdb = None
        self.tmdb = None
        self.tvdb = None
        self.title_type = None
        self.title_type_name = None
        self.title_name = None
        self.title_year = None
        self.season = None
        self.episode = None
        self.episode_name = None
        self.episodes = None
        self.release_name = None
        self.preview_url = None
        self.source = None
        self.note = None
        self.videos = None
        self.audio = None
        self.subtitles = None
        self.chapters = None
        self.chapters_numbered = None

    def __repr__(self):
        return "<{c} {attrs}>".format(
            c=self.__class__.__name__,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def setConfig(self, config):
        # Ensure config isn't empty
        if not config:
            raise ValueError("NFO.applyConfig: Parameter config's data is null or empty...")
        # Get Art Template
        self.art = config["art"]
        # Get input file path
        self.file = anti_file_prefix(config["file"])
        # Get Database ID's
        self.imdb, self.tmdb, self.tvdb = self.getDatabaseIds(config)
        # Get Title Type, Name, and Year
        self.title_type, self.title_type_name = self.getTitleType(config)
        self.title_name, self.title_year = self.getTitleNameYear()
        # Get TV Season, Episode, and Episode Name information
        self.season, self.episode, self.episode_name = self.getTvInfo(config)
        self.episodes = self.getTvEpisodes()
        # Get Release Name
        self.release_name = self.getReleaseName()
        # Get Preview Url
        self.preview_url = config["preview-url"]
        # Get Source and Note
        self.source = config["source"]
        self.note = config["note"]
        # Get Tracks
        self.videos = self.getTracks("Video")
        self.audio = self.getTracks("Audio")
        self.subtitles = self.getTracks("Text")
        self.chapters = [v for k, v in self.getTracks("Menu")[0].to_data().items() if ("1" + k.replace("_", "")).isdigit()]
        self.chapters_numbered = sum(
            1 for i, x in enumerate(self.chapters) if x.split(":", 1)[-1] in [f"Chapter {i+1}", f"Chapter {str(i+1).zfill(2)}"]
        ) == len(self.chapters)
        print(self)

    def getDatabaseIds(self, config):
        general = self.getTracks("General")[0].to_data()
        dbs = {"imdb": None, "tmdb": None, "tvdb": None}
        for db in dbs.keys():
            if db in general and general[db]:
                dbs[db] = general[db]
            elif db in config and config[db]:
                dbs[db] = config[db]
        if not dbs["imdb"]:
            while not dbs["imdb"]:
                dbs["imdb"] = input("An IMDB ID is required but wasn't found, what's it's IMDb ID?\n")
            dbs["tmdb"] = input("While we're at it, does this title have a TMDB ID?\n") or None
            dbs["tvdb"] = input("What about a TVDB ID?\n") or None
        for k, v in dbs.items():
            if not v:
                print(f"Warning: No {k} ID was found...")
        return dbs.values()

    def getTitleType(self, config) -> tuple:
        name_map = {
            "season": "TV Series",
            "episode": "TV Series",
            "movie": "Movie"
        }
        if self.imdb and self.tmdb and not self.tvdb:
            return "movie", name_map["movie"]
        return config["type"], name_map[config["type"]]

    def getTitleNameYear(self) -> tuple:
        imdb_page = scrape(f"https://www.imdb.com/title/{self.imdb}")
        imdb_title = re.search(
            # testing ground: https://regex101.com/r/dRpT6g/1
            r"<title>(?P<name>.+) \(((?P<type>TV (Movie|Series|Mini-Series) |)(?P<year>(\d{4})(|– |–\d{4})))\) - IMDb<\/title>",
            imdb_page
        )
        if not imdb_title:
            raise ValueError("Could not scrape Movie Title or Year...")
        return imdb_title.group("name"), imdb_title.group("year")

    def getTvInfo(self, config) -> tuple:
        general = self.getTracks("General")[0]
        if general.title:
            tv_title = re.search("^.*? S(\\d+)E(\\d+) (.*)$", general.title)
            if tv_title:
                season, episode, episode_name = tv_title.groups()
                return int(season), int(episode), episode_name
        if self.title_type == "season":
            season = None
            if "season" in config and config["season"]:
                season = config["season"]
            while not season:
                input("What Season is this release for? e.g. `5`, `V01`, `1-4`, `0`, `Specials`:\n")
            return season, None, None
        if self.title_type == "episode":
            season = None
            if "season" in config and config["season"]:
                season = config["season"]
            while not season:
                season = input("What Season is this release for? e.g. `5`, `V01`, `1-4`, `0`, `Specials`:\n")
            episode = None
            if "episode" in config and config["episode"]:
                episode = config["episode"]
            while not episode:
                episode = int(input("Ok great, what Episode?:\n"))
            episode_name = None
            if "episode-name" in config and config["episode-name"]:
                episode_name = config["episode-name"]
            while not episode_name:
                episode_name = input("Alright, what's the Episode Name/Title?:\n")
            return season, episode, episode_name
        return None, None, None

    def getTvEpisodes(self) -> int:
        # Calculate total episode count (presumably of the season) by counting neighbouring media files
        if self.title_type != "season":
            return 0
        return len(glob.glob(os.path.join(
            os.path.dirname(self.file),
            f"*{os.path.splitext(self.file)[-1]}"
        )))

    def getReleaseName(self) -> str:
        # Retrieve the release name based on the input file or parent folder
        if self.title_type == "season":
            return os.path.basename(os.path.dirname(self.file))
        return os.path.splitext(os.path.basename(self.file))[0]

    def getMediaInfo(self):
        self.media_info = MediaInfo.parse(self.file)
        """
        general = self.getTracks("General")[0]
        videos = self.getTracks("Video")
        audios = self.getTracks("Audio")
        subtitles = self.getTracks("Text")
        chapters = self.getTracks("Menu")
        chapters_numbered = False
        """

    def getTracks(self, type=None):
        if not self.media_info:
            self.getMediaInfo()
        return [track for track in self.media_info.tracks if not type or track.track_type == type]

    def getVideoPrint(self, videos) -> list:
        if not videos:
            return ["--"]
        data = []
        for t in videos:
            codec = {
                "MPEG Video": f"MPEG-{t.format_version.replace('Version ', '')}"
            }.get(t.format, t.format)
            interlaced_percent = None
            vst = False
            if codec in ["MPEG-1", "MPEG-2"]:
                # make sure a d2v file for this video exists
                self.file = get_d2v(self.file)
                # parse d2v file with pyd2v
                d2v = D2V(self.file)
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
                    os.unlink(os.path.splitext(self.file)[0] + "." + ext)
            l1 = f"- {pycountry.languages.get(alpha_2=t.language).name}, {codec} " + \
                f"({t.format_profile}) {t.width}x{t.height} ({t.other_display_aspect_ratio[0]}) " + \
                f"@ {t.other_bit_rate[0]}{f' ({t.bit_rate_mode})' if t.bit_rate_mode else ''}"
            l2 = f"  {(f'{t.framerate_num}/{t.framerate_den}' if t.framerate_num else t.frame_rate)} FPS " + \
                 f"({'VFR' if vst else t.frame_rate_mode}), {t.color_space}{t.chroma_subsampling.replace(':', '')}" + \
                 f"P{t.bit_depth}, {interlaced_percent if interlaced_percent else t.scan_type}"
            data.append([l1, l2])
        return data

    def getAudioPrint(self, audio) -> list:
        if not audio:
            return ["--"]
        data = []
        for t in audio:
            if t.title and "Commentary" in t.title:
                title = t.title
            else:
                title = pycountry.languages.get(alpha_2=t.language).name
            channels = float(sum(self.AUDIO_CHANNEL_LAYOUT_WEIGHT.get(x, 1) for x in t.channel_layout.split(" ")))
            bit_rate_mode = f" ({t.bit_rate_mode})" if t.bit_rate_mode else ""
            l1 = f"- {title}, {t.format} {channels} @ {t.other_bit_rate[0]}{bit_rate_mode}"
            data += [("  " + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(l1, 64))]
        return data

    @staticmethod
    def getSubtitlePrint(subs):
        if not subs:
            return ["--"]
        data = []
        for t in subs:
            title = t.title or pycountry.languages.get(alpha_2=t.language).name
            l1 = f"- {title}, {t.format.replace('UTF-8', 'SubRip (SRT)')}"
            data += [("  " + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(l1, 64))]
        return data

    @staticmethod
    def getChapterPrint(chapters):
        return ["--"] if not chapters else [[
            f"- {v}"
        ] for v in chapters]

    def getChapterPrintShort(self, chapters):
        if not chapters:
            return "No"
        if self.chapters_numbered:
            return f"Yes (Numbered 01-{str(len(chapters)).zfill(2)})"
        return f"Yes (Named)"

    def getVariable(self, name):
        val = self.__dict__[self.TEMPLATE_VAR_TO_CLASS_VAR_MAP[name]]
        if name == "releaseName":
            return [x.center(70) for x in textwrap.wrap(val, 68)]
        if name in ["source", "note"]:
            return textwrap.wrap(val, 68) if val else None
        if name == "videoTracks":
            return self.getVideoPrint(val)
        if name == "audioTracks":
            return self.getAudioPrint(val)
        if name == "subtitleTracks":
            return self.getSubtitlePrint(val)
        if name == "chapters":
            return self.getChapterPrintShort(val)
        if name == "chapterEntries":
            return self.getChapterPrint(val)
        if name == "chaptersNamed":
            return val and not self.chapters_numbered
        if name in ["videoTrackCount", "audioTrackCount", "subtitleTrackCount", "chaptersCount"]:
            return len(val)
        return val

    def getVariables(self):
        return self.TEMPLATE_VAR_TO_CLASS_VAR_MAP.keys()
