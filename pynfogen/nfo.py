import glob
import html
import os
import re
import textwrap
from pathlib import Path
from typing import List, Union, Tuple, Optional, Any, Dict

import pycountry
import requests
from pyd2v import D2V
from pymediainfo import MediaInfo, Track

from pynfogen.formatter import CustomFormats


class NFO:
    AUDIO_CHANNEL_LAYOUT_WEIGHT = {
        "LFE": 0.1
    }
    SEASON_T = Optional[Union[int, str]]
    EPISODE_T = Optional[Union[Tuple[Optional[int], Optional[str]]]]
    IMDB_ID_T = re.compile(r"^tt\d{7,8}$")
    TMDB_ID_T = re.compile(r"^(tv|movie)/\d+$")
    TVDB_ID_T = re.compile(r"^\d+$")

    def __init__(self) -> None:
        self.media_info: MediaInfo

        self.file: str
        self.season: Optional[Union[int, str]]
        self.episode: Optional[int]
        self.episode_name: Optional[str]

        self.videos: List[Track]
        self.audio: List[Track]
        self.subtitles: List[Track]
        self.chapters: Dict[str, str]
        self.chapters_numbered: bool

        self.fanart_api_key: Optional[str]
        self.source: Optional[str]
        self.note: Optional[str]
        self.preview: Optional[str]

        self.imdb: str
        self.tmdb: Optional[str]
        self.tvdb: Optional[int]

        self.title_name: str
        self.title_year: str
        self.episodes: int
        self.release_name: str
        self.preview_images: List[dict[str, str]]
        self.banner_image: Optional[str]

        self.session = self.get_session()

    def __repr__(self) -> str:
        return "<{c} {attrs}>".format(
            c=self.__class__.__name__,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def run(self, template: str, art: Optional[str] = None, **kwargs: Any) -> str:
        """
        Evaluate and apply formatting on template, apply any art if provided.
        Any additional parameters are passed as extra variables to the template.
        The extra variables have priority when there's conflicting variable names.
        """
        variables = self.__dict__
        variables.update(kwargs)

        template = CustomFormats().format(template, **variables)
        if art:
            art = art.format(nfo=template)
            template = art

        for m in re.finditer(r"<\?([01])\?([\D\d]*?)\?>", template):
            # TODO: This if check is quite yucky, look into alternative options.
            #       Ideally a custom format spec would be great.
            template = template.replace(
                m.group(0),
                m.group(2) if int(m.group(1)) else ""
            )

        template = "\n".join(map(str.rstrip, template.splitlines(keepends=False)))

        return template

    def set_config(self, file: str, season: SEASON_T, episode: EPISODE_T, **config: Any) -> None:
        if not config or not isinstance(config, dict):
            raise ValueError("NFO.set_config: Parameter config is empty or not a dictionary...")

        self.file = file
        self.media_info = MediaInfo.parse(self.file)

        self.fanart_api_key = config.get("fanart_api_key")
        self.source = config.get("source")
        self.note = config.get("note")
        self.preview = config.get("preview")

        self.season = season
        self.episode, self.episode_name = episode or (None, None)
        self.episodes = self.get_tv_episodes()
        self.release_name = self.get_release_name()

        self.videos = self.media_info.video_tracks
        self.audio = self.media_info.audio_tracks
        self.subtitles = self.media_info.text_tracks

        chapters = next(iter(self.media_info.menu_tracks), None)
        if chapters:
            self.chapters = {
                ".".join([k.replace("_", ".")[:-3], k[-3:]]): v.strip(":")
                for k, v in chapters.to_data().items()
                if f"1{k.replace('_', '')}".isdigit()
            }
            self.chapters_numbered = all(
                x.split(":", 1)[-1].lower() in [f"chapter {i + 1}", f"chapter {str(i + 1).zfill(2)}"]
                for i, x in enumerate(self.chapters.values())
            )
        else:
            self.chapters = {}
            self.chapters_numbered = False

        self.imdb = self.get_imdb_id(config)
        self.tmdb = self.get_tmdb_id(config)
        self.tvdb = self.get_tvdb_id(config)

        self.title_name, self.title_year = self.get_title_name_year()
        self.banner_image = self.get_banner_image(self.tvdb) if self.tvdb else None
        self.preview_images = self.get_preview_images(self.preview) if self.preview else []

        print(self)

    def get_imdb_id(self, config: dict) -> str:
        """
        Get an IMDB ID from either the media's global tags, or the config.
        Since IMDB IDs are required for this project, it will bug the user for
        one interactively if not found.
        """
        general_track = self.media_info.general_tracks[0].to_data()
        imdb_id = general_track.get("imdb") or config.get("imdb")
        if not imdb_id:
            print("No IMDB ID was provided but is required...")
        while not imdb_id:
            user_id = input("IMDB ID (e.g., 'tt0487831'): ")
            if not self.IMDB_ID_T.match(user_id):
                print(f"The provided IMDB ID '{user_id}' is not valid...")
                print("Expected e.g., 'tt0487831', 'tt10810424', (include the 'tt').")
            else:
                imdb_id = user_id
        return imdb_id

    def get_tmdb_id(self, config: dict) -> Optional[str]:
        """
        Get a TMDB ID from either the media's global tags, or the config.
        It will raise a ValueError if the provided ID is invalid.
        """
        general_track = self.media_info.general_tracks[0].to_data()
        tmdb_id = general_track.get("tmdb") or config.get("tmdb") or None
        if not tmdb_id:
            print("Warning: No TMDB ID was provided...")
            return None
        if not self.TMDB_ID_T.match(tmdb_id):
            print(f"The provided TMDB ID '{tmdb_id}' is not valid...")
            print("Expected e.g., 'tv/2490', 'movie/14836', (include the 'tv/' or 'movie/').")
            raise ValueError("Invalid TMDB ID")
        return tmdb_id

    def get_tvdb_id(self, config: dict) -> Optional[int]:
        """
        Get a TVDB ID from either the media's global tags, or the config.
        It will raise a ValueError if the provided ID is invalid.
        """
        general_track = self.media_info.general_tracks[0].to_data()
        tvdb_id = general_track.get("tvdb") or config.get("tvdb") or None
        if not tvdb_id:
            print("Warning: No TVDB ID was provided...")
            return None
        if not self.TVDB_ID_T.match(tvdb_id):
            print(f"The provided TVDB ID '{tvdb_id}' is not valid...")
            print("Expected e.g., '79216', '1395', (not the url slug e.g., 'the-office-us').")
            raise ValueError("Invalid TVDB ID")
        return int(tvdb_id)

    def get_title_name_year(self) -> Tuple[str, str]:
        """Scrape Title Name and Year (including e.g. 2019-) from IMDB"""
        r = self.session.get(f"https://www.imdb.com/title/{self.imdb}")
        if r.status_code != 200:
            raise ValueError(f"An unexpected error occurred getting IMDB Title Page [{r.status_code}]")
        imdb_page = html.unescape(r.text)
        imdb_title = re.search(
            # testing ground: https://regex101.com/r/bEoEDn/1
            r"<title>(?P<name>.+) \(((?P<type>TV (Movie|Series|Mini[- ]Series|Short|Episode) |Video |Short |)"
            r"(?P<year>(\d{4})(|– |–\d{4})))\) - IMDb</title>",
            imdb_page
        )
        if not imdb_title:
            raise ValueError(f"Could not scrape Movie Title or Year for {self.imdb}...")
        return imdb_title.group("name").strip(), imdb_title.group("year").strip()

    def get_tv_episodes(self) -> int:
        """Calculate total episode count based on neighbouring same-extension files."""
        return len(glob.glob(os.path.join(
            os.path.dirname(self.file),
            f"*{os.path.splitext(self.file)[-1]}"
        )))

    def get_release_name(self) -> str:
        """
        Retrieve the release name based on the file used during MediaInfo.
        If a season was specified, but an episode number was not, it presumes the release is a Pack.
        Hence when pack, it uses the parent folder's name as the release name.
        """
        if self.season is not None and self.episode is None:
            return os.path.basename(os.path.dirname(self.file))
        return os.path.splitext(os.path.basename(self.file))[0]

    def get_banner_image(self, tvdb_id: int) -> Optional[str]:
        """
        Get a wide banner image from fanart.tv.
        Currently restricts banners to English-only.
        """
        if not tvdb_id:
            return None
        if not self.fanart_api_key:
            raise ValueError("Need Fanart.tv api key for TV titles!")

        r = self.session.get(f"http://webservice.fanart.tv/v3/tv/{tvdb_id}?api_key={self.fanart_api_key}")
        if r.status_code == 404:
            return None
        res = r.json()

        error = res.get("error message")
        if error:
            if error == "Not found":
                return None
            raise ValueError(f"An unexpected error occurred while calling Fanart.tv, {res}")

        banner = next((
            x["url"] for x in (res.get("tvbanner") or [])
            if x["lang"] == sorted(self.audio, key=lambda x: x.streamorder)[0].language
        ), None)

        return banner

    def get_preview_images(self, url: str) -> List[Dict[str, str]]:
        if not url:
            return []
        images = []
        for domain in ["imgbox.com", "beyondhd.co"]:
            if domain not in url.lower():
                continue
            page = self.session.get(url).text
            if domain == "imgbox.com":
                for m in re.finditer('src="(https://thumbs2.imgbox.com.+/)(\\w+)_b.([^"]+)', page):
                    images.append({
                        "url": f"https://imgbox.com/{m.group(2)}",
                        "src": f"{m.group(1)}{m.group(2)}_t.{m.group(3)}"
                    })
            elif domain == "beyondhd.co":
                for m in re.finditer('/image/([^"]+)"\\D+src="(https://.*beyondhd.co/images.+/(\\w+).md.[^"]+)', page):
                    images.append({
                        "url": f"https://beyondhd.co/image/{m.group(1)}",
                        "src": m.group(2)
                    })
            break
        return images

    def get_video_print(self, videos: List[Track]) -> List[List[str]]:
        if not videos:
            return [["--"]]
        data = []
        for video in videos:
            codec = {
                "MPEG Video": f"MPEG-{(video.format_version or '').replace('Version ', '')}"
            }.get(video.format, video.format)
            scan_overview = video.scan_type
            vst = False
            if codec in ["MPEG-1", "MPEG-2"]:
                # parse d2v file with pyd2v, generates D2V if needed
                d2v = D2V.load(Path(self.file))
                self.file = d2v.path
                # get every frames' flag data, this contains information on displaying frames
                # add vob and cell number to each frames flag data as well
                flags = [f for line in [
                    [dict(**y, vob=x["vob"], cell=x["cell"]) for y in x["flags"]] for x in d2v.data
                ] for f in line]
                interlaced_percent = (sum(1 for f in flags if not f["progressive_frame"]) / len(flags)) * 100
                if interlaced_percent == 100:
                    scan_overview = "Interlaced (CST)"
                else:
                    scan_overview = f"{round(interlaced_percent, 2)}% Interlaced (VST)"
                    vst = True
                for ext in ["log", "d2v", "mpg", "mpeg"]:
                    fp = os.path.splitext(self.file)[0] + "." + ext
                    if os.path.exists(fp):
                        os.unlink(fp)
            line_1 = "- {language}, {codec} ({profile}) {width}x{height} ({aspect}) @ {bitrate}".format(
                language=pycountry.languages.get(alpha_2=video.language).name,
                codec=codec,
                profile=video.format_profile,
                width=video.width, height=video.height,
                aspect=video.other_display_aspect_ratio[0],
                bitrate=f"{video.other_bit_rate[0]}{f' ({video.bit_rate_mode})' if video.bit_rate_mode else ''}"
            )
            line_2 = "  {fps} FPS ({fps_mode}), {color_space}{subsampling}P{bit_depth}, {scan}".format(
                fps=f"{video.framerate_num}/{video.framerate_den}" if video.framerate_num else video.frame_rate,
                fps_mode="VFR" if vst else video.frame_rate_mode,
                color_space=video.color_space,
                subsampling=video.chroma_subsampling.replace(":", ""),
                bit_depth=video.bit_depth,
                scan=scan_overview
            )
            data.append([line_1, line_2])
        return data

    def get_audio_print(self, audio: List[Track]) -> List[str]:
        if not audio:
            return ["--"]
        data = []
        for t in audio:
            if t.title and "Commentary" in t.title:
                title = t.title
            else:
                title = pycountry.languages.get(alpha_2=t.language).name
            if t.channel_layout:
                channels = float(sum(self.AUDIO_CHANNEL_LAYOUT_WEIGHT.get(x, 1) for x in t.channel_layout.split(" ")))
            else:
                channels = float(t.channel_s)
            bit_rate_mode = f" ({t.bit_rate_mode})" if t.bit_rate_mode else ""
            l1 = f"- {title}, {t.format} {channels} @ {t.other_bit_rate[0]}{bit_rate_mode}"
            data += [("  " + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(l1, 64))]
        return data

    @staticmethod
    def get_subtitle_print(subs: List[Track]) -> List[str]:
        """
        Return a list of a brief subtitle overview per-subtitle.

        e.g.
        - English, Forced, SubRip (SRT)
        - English, SubRip (SRT)
        - English, SDH, SubRip (SRT)
        - Spanish, Latin American (SDH), SubRip (SRT)

        The bit of text between the Language and the Subtitle format is the Track Title.
        It can be of any format, but it is recommended to be used as shown above.

        It will be returned as a list of strings with the `- ` already pre-pended to each entry.
        """
        data = []
        if not subs:
            data.append("--")
        for sub in subs:
            line_items = []

            # following sub.title tree checks and supports three different language and title scenarios
            # The second scenario is the recommended option to choose if you are open to choosing any
            # The third scenario should be used if you have nothing unique to state about the track
            # | Language     | Track Title                   | Output                                        |
            # | ------------ | ----------------------------- | --------------------------------------------- |
            # | es / Spanish | Spanish (Latin American, SDH) | - Spanish (Latin American, SDH), SubRip (SRT) |
            # | es / Spanish | Latin American (SDH)          | - Spanish, Latin American (SDH), SubRip (SRT) |
            # | es / Spanish | None                          | - Spanish, SubRip (SRT)                       |
            language = pycountry.languages.get(alpha_2=sub.language).name
            if sub.title:
                if language.lower() in sub.title.lower():
                    line_items.append(sub.title)
                else:
                    line_items.append(f"{language}, {sub.title}")
            else:
                line_items.append(language)

            line_items.append(sub.format.replace("UTF-8", "SubRip (SRT)"))

            line = "- " + ", ".join(line_items)
            data += [
                ("  " + x if i > 0 else x)
                for i, x in enumerate(textwrap.wrap(line, 64))
            ]
        return data

    @staticmethod
    def get_chapter_print(chapters: Dict[str, str]) -> List[str]:
        if not chapters:
            return ["--"]
        return [
            f"- {k}: {v}"
            for k, v in chapters.items()
        ]

    def get_chapter_print_short(self, chapters: Dict[str, str]) -> str:
        if not chapters:
            return "No"
        if self.chapters_numbered:
            return f"Yes (Numbered 01-{str(len(chapters)).zfill(2)})"
        return "Yes (Named)"

    @staticmethod
    def get_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "UPGRADE-INSECURE-REQUESTS": "1"
        })
        return session
